#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path

import chess
import chess.pgn
import chess.engine


def score_cp(score, turn):
    pov = score.pov(turn)
    if pov.is_mate():
        m = pov.mate()
        return 100000 if m and m > 0 else -100000
    return pov.score(mate_score=100000)


def evaluation_loss(best_score, played_score, mover, played_board=None):
    """Return a training-oriented loss without treating mate scores as centipawns.

    Mate scores are ordinal, not material values. Mapping M1/M0 to +/-100000 and
    subtracting them can make a mating move look like a 200000-cp blunder. This
    helper keeps ordinary centipawn loss for non-mating positions, while handling
    forced mates explicitly.
    """
    # A legal move that ends the game by checkmate cannot be an error.
    if played_board is not None and played_board.is_checkmate():
        return 0

    best_pov = best_score.pov(mover)
    played_pov = played_score.pov(mover)
    best_mate = best_pov.mate() if best_pov.is_mate() else None
    played_mate = played_pov.mate() if played_pov.is_mate() else None

    # If both lines preserve the same mate outcome, do not fabricate a huge CPL
    # from mate distance. For training purposes, preserving a forced win (or an
    # already forced loss) is not a centipawn error.
    if best_mate is not None and played_mate is not None:
        if best_mate > 0 and played_mate > 0:
            return 0
        if best_mate < 0 and played_mate < 0:
            return 0

    # Losing a forced mate, or allowing a forced mate that the best move avoids,
    # is unequivocally a blunder. 1000 cp is enough to classify it without using
    # artificial 100000/200000-cp arithmetic.
    if best_mate is not None and best_mate > 0:
        if played_mate is None or played_mate <= 0:
            return 1000
    if played_mate is not None and played_mate < 0:
        if best_mate is None or best_mate >= 0:
            return 1000

    # Search noise can occasionally compare a forced-loss score with a non-mate
    # score. Avoid turning that engine-boundary effect into a fake giant error.
    if best_mate is not None or played_mate is not None:
        return 0

    best_cp = best_pov.score()
    played_cp = played_pov.score()
    if best_cp is None or played_cp is None:
        return 0
    return max(0, best_cp - played_cp)


def fmt_eval(score, turn):
    pov = score.pov(turn)
    if pov.is_mate():
        m = pov.mate()
        return f"M{m}" if m is not None else "mate"
    cp = pov.score(mate_score=100000) or 0
    return f"{cp/100:+.2f}"


def classify_loss(loss_cp):
    if loss_cp >= 300:
        return "blunder"
    if loss_cp >= 150:
        return "mistake"
    if loss_cp >= 70:
        return "inaccuracy"
    return "ok"


def first_info(result):
    return result[0] if isinstance(result, list) else result


def analyse(engine, board, depth, multipv=1):
    result = engine.analyse(board, chess.engine.Limit(depth=depth), multipv=multipv)
    if isinstance(result, list):
        return result
    return [result]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pgn")
    ap.add_argument("--depth", type=int, default=20, help="Deep verification depth")
    ap.add_argument("--scan-depth", type=int, default=14, help="Fast first-pass depth")
    ap.add_argument("--multipv", type=int, default=3)
    ap.add_argument("--verify-threshold", type=int, default=40,
                    help="Deep-verify moves whose scan CPL reaches this value")
    ap.add_argument("--stockfish", default=os.environ.get("STOCKFISH_PATH", "/usr/games/stockfish"))
    ap.add_argument("--outdir", default="analysis")
    args = ap.parse_args()

    pgn_path = Path(args.pgn)
    with pgn_path.open(encoding="utf-8") as f:
        game = chess.pgn.read_game(f)
    if game is None:
        raise SystemExit("No valid PGN found")

    moves = list(game.mainline_moves())

    # Build every position once. positions[i] is the board before move i,
    # positions[-1] is the final position. This lets the scan reuse the
    # evaluation after one move as the evaluation before the next move.
    positions = [game.board()]
    board = game.board()
    sans = []
    for move in moves:
        sans.append(board.san(move))
        board = board.copy(stack=False)
        board.push(move)
        positions.append(board)

    engine = chess.engine.SimpleEngine.popen_uci(args.stockfish)
    try:
        # Sensible GitHub-hosted-runner defaults. Ignore options an engine/build
        # does not expose rather than making analysis fail.
        options = {}
        if "Threads" in engine.options:
            options["Threads"] = 2
        if "Hash" in engine.options:
            options["Hash"] = 256
        if options:
            engine.configure(options)

        # PASS 1: one inexpensive single-PV search per unique game position.
        # Old implementation did two searches per ply, half of them MultiPV 3.
        scan = []
        for pos in positions:
            scan.append(first_info(analyse(engine, pos, args.scan_depth, 1)))

        rows = []
        counts = {"blunder": 0, "mistake": 0, "inaccuracy": 0}
        verified_count = 0

        for i, move in enumerate(moves):
            ply = i + 1
            pre = positions[i]
            post = positions[i + 1]
            mover = pre.turn

            scan_before = scan[i]
            scan_after = scan[i + 1]
            scan_loss = evaluation_loss(
                scan_before["score"], scan_after["score"], mover, post
            )

            # Verify anything reasonably close to our first classification
            # threshold so subtle inaccuracies are less likely to be missed.
            # Ordinary moves stay cheap while critical moves get the full
            # depth-20 + MultiPV treatment used by the original lab.
            deep_verify = scan_loss >= args.verify_threshold

            if deep_verify:
                verified_count += 1
                before = analyse(engine, pre, args.depth, args.multipv)
                after = first_info(analyse(engine, post, args.depth, 1))
                best = before[0]
                loss = evaluation_loss(best["score"], after["score"], mover, post)
                best_eval = fmt_eval(best["score"], chess.WHITE)
                played_eval = fmt_eval(after["score"], chess.WHITE)
                analysis_depth = args.depth
                alternatives = []
                for info in before[: args.multipv]:
                    pv = info.get("pv", [])
                    if not pv:
                        continue
                    alternatives.append({
                        "move": pre.san(pv[0]),
                        "eval_white": fmt_eval(info["score"], chess.WHITE),
                    })
            else:
                best = scan_before
                after = scan_after
                loss = scan_loss
                best_eval = fmt_eval(best["score"], chess.WHITE)
                played_eval = fmt_eval(after["score"], chess.WHITE)
                analysis_depth = args.scan_depth
                pv = best.get("pv", [])
                alternatives = []
                if pv:
                    alternatives.append({
                        "move": pre.san(pv[0]),
                        "eval_white": best_eval,
                    })

            best_move = best.get("pv", [None])[0]
            best_san = pre.san(best_move) if best_move else None
            cls = classify_loss(loss)
            if cls in counts:
                counts[cls] += 1

            rows.append({
                "ply": ply,
                "move_number": (ply + 1) // 2,
                "side": "White" if mover == chess.WHITE else "Black",
                "played": sans[i],
                "best": best_san,
                "eval_before_white": best_eval,
                "eval_after_white": played_eval,
                "centipawn_loss": loss,
                "classification": cls,
                "analysis_depth": analysis_depth,
                "deep_verified": deep_verify,
                "alternatives": alternatives,
            })
    finally:
        engine.quit()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    stem = pgn_path.stem
    json_path = outdir / f"{stem}.json"
    md_path = outdir / f"{stem}.md"

    payload = {
        "headers": dict(game.headers),
        "engine": "Stockfish 18 NNUE",
        "analysis_mode": "two-pass",
        "scan_depth": args.scan_depth,
        "depth": args.depth,
        "multipv": args.multipv,
        "verify_threshold_cp": args.verify_threshold,
        "deep_verified_moves": verified_count,
        "summary": counts,
        "moves": rows,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        f"# Stockfish analysis — {stem}",
        "",
        f"Mode: **two-pass** · Scan depth: **{args.scan_depth}** · Critical depth: **{args.depth}** · MultiPV: **{args.multipv}**",
        "",
        f"Deep-verified moves: **{verified_count}/{len(moves)}**",
        "",
        f"Blunders: **{counts['blunder']}** · Mistakes: **{counts['mistake']}** · Inaccuracies: **{counts['inaccuracy']}**",
        "",
        "| Move | Played | Best | Eval after | CPL | Class | Depth |",
        "|---:|---|---|---:|---:|---|---:|",
    ]
    for r in rows:
        prefix = f"{r['move_number']}." if r["side"] == "White" else f"{r['move_number']}..."
        depth_label = f"{r['analysis_depth']}*" if r["deep_verified"] else str(r["analysis_depth"])
        md.append(
            f"| {prefix} | {r['played']} | {r['best'] or '-'} | {r['eval_after_white']} | "
            f"{r['centipawn_loss']} | {r['classification']} | {depth_label} |"
        )

    md.extend([
        "",
        f"`*` Deep-verified at depth {args.depth}; ordinary moves use the depth-{args.scan_depth} scan.",
    ])

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Two-pass analysis: {len(moves)} plies, {verified_count} deep-verified")
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
