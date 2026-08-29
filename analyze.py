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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pgn")
    ap.add_argument("--depth", type=int, default=18)
    ap.add_argument("--multipv", type=int, default=3)
    ap.add_argument("--stockfish", default=os.environ.get("STOCKFISH_PATH", "/usr/games/stockfish"))
    ap.add_argument("--outdir", default="analysis")
    args = ap.parse_args()

    pgn_path = Path(args.pgn)
    with pgn_path.open(encoding="utf-8") as f:
        game = chess.pgn.read_game(f)
    if game is None:
        raise SystemExit("No valid PGN found")

    engine = chess.engine.SimpleEngine.popen_uci(args.stockfish)
    board = game.board()
    rows = []
    counts = {"blunder": 0, "mistake": 0, "inaccuracy": 0}

    try:
        moves = list(game.mainline_moves())
        for ply, move in enumerate(moves, start=1):
            mover = board.turn
            san = board.san(move)
            before = engine.analyse(board, chess.engine.Limit(depth=args.depth), multipv=args.multipv)
            if not isinstance(before, list):
                before = [before]
            best = before[0]
            best_move = best.get("pv", [None])[0]
            best_san = board.san(best_move) if best_move else None
            best_cp = score_cp(best["score"], mover)
            best_eval = fmt_eval(best["score"], chess.WHITE)

            board.push(move)
            after = engine.analyse(board, chess.engine.Limit(depth=args.depth))
            played_cp = score_cp(after["score"], mover)
            played_eval = fmt_eval(after["score"], chess.WHITE)
            loss = max(0, best_cp - played_cp)
            cls = classify_loss(loss)
            if cls in counts:
                counts[cls] += 1

            alternatives = []
            pre = game.board()
            for previous in moves[: ply - 1]:
                pre.push(previous)
            for info in before[: args.multipv]:
                pv = info.get("pv", [])
                if not pv:
                    continue
                alternatives.append({
                    "move": pre.san(pv[0]),
                    "eval_white": fmt_eval(info["score"], chess.WHITE),
                })

            rows.append({
                "ply": ply,
                "move_number": (ply + 1) // 2,
                "side": "White" if mover == chess.WHITE else "Black",
                "played": san,
                "best": best_san,
                "eval_before_white": best_eval,
                "eval_after_white": played_eval,
                "centipawn_loss": loss,
                "classification": cls,
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
        "depth": args.depth,
        "multipv": args.multipv,
        "summary": counts,
        "moves": rows,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        f"# Stockfish analysis — {stem}",
        "",
        f"Depth: **{args.depth}** · MultiPV: **{args.multipv}**",
        "",
        f"Blunders: **{counts['blunder']}** · Mistakes: **{counts['mistake']}** · Inaccuracies: **{counts['inaccuracy']}**",
        "",
        "| Move | Played | Best | Eval after | CPL | Class |",
        "|---:|---|---|---:|---:|---|",
    ]
    for r in rows:
        prefix = f"{r['move_number']}." if r["side"] == "White" else f"{r['move_number']}..."
        md.append(f"| {prefix} | {r['played']} | {r['best'] or '-'} | {r['eval_after_white']} | {r['centipawn_loss']} | {r['classification']} |")

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json_path)
    print(md_path)


if __name__ == "__main__":
    main()
