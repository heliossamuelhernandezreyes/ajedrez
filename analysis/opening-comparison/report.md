# Stockfish 18: exploratory opening comparison

Depth 16. Positive = White advantage. Black moves are scripted by repertoire; White replies are Stockfish choices. If scripted move is illegal, Black uses Stockfish best. **Not an optimized repertoire tournament**.

| White start | Hybrid | Pirc-like | French-like | Caro-like |
|---|---:|---:|---:|---:|
| King pawn | 0.77 | 0.75 | 0.49 | 0.38 |
| Queen pawn | 0.86 | 0.53 | 0.48 | 0.98 |
| English | 0.92 | 0.65 | 0.23 | 0.94 |
| Reti | 0.94 | 0.64 | 0.11 | 4.51 |
| Bird | 0.72 | 0.66 | 0.27 | 3.78 |
| Larsen | 0.46 | 0.15 | 0.04 | 0.32 |
| Nimzo-Larsen | 0.76 | 0.8 | 0.42 | 4.37 |
| King fianchetto | 0.69 | 0.5 | 0.37 | -0.08 |
| Sokolsky | 0.16 | 0.25 | -0.18 | 0.0 |
| Van Geet flank | 0.66 | 0.31 | 0.06 | 0.22 |
| King-side pawn | 0.39 | 0.49 | 1.0 | 0.92 |
| Grob | 0.2 | 0.13 | -0.66 | 4.05 |

## Complete tested continuations

| White | Black repertoire | Moves (SAN tokens, alternating from White) | White eval | Script substitutions |
|---|---|---|---:|---|
| King pawn | Your hybrid | e4 d6 d4 e6 Nf3 Nf6 Bd3 | 0.77 | none |
| King pawn | Pirc-like | e4 d6 d4 Nf6 Nc3 g6 Bf4 | 0.75 | none |
| King pawn | French-like | e4 e6 d4 d5 Nc3 Nf6 e5 | 0.49 | none |
| King pawn | Caro-like | e4 c6 d4 d5 e5 Bf5 h4 | 0.38 | none |
| Queen pawn | Your hybrid | d4 d6 e4 e6 Nf3 Nf6 Bd3 | 0.86 | none |
| Queen pawn | Pirc-like | d4 d6 Nf3 Nf6 c4 g6 Nc3 | 0.53 | none |
| Queen pawn | French-like | d4 e6 e4 d5 Nc3 Nf6 e5 | 0.48 | none |
| Queen pawn | Caro-like | d4 c6 Nf3 d5 c4 Bf5 cxd5 | 0.98 | none |
| English | Your hybrid | c4 d6 Nc3 e6 d4 Nf6 e4 | 0.92 | none |
| English | Pirc-like | c4 d6 Nc3 Nf6 d4 g6 e4 | 0.65 | none |
| English | French-like | c4 e6 d4 d5 Nc3 Nf6 cxd5 | 0.23 | none |
| English | Caro-like | c4 c6 Nf3 d5 d4 Bf5 cxd5 | 0.94 | none |
| Reti | Your hybrid | Nf3 d6 e4 e6 d4 Nf6 Bd3 | 0.94 | none |
| Reti | Pirc-like | Nf3 d6 d4 Nf6 c4 g6 Nc3 | 0.64 | none |
| Reti | French-like | Nf3 e6 c4 d5 d4 Nf6 Bg5 | 0.11 | none |
| Reti | Caro-like | Nf3 c6 Nc3 d5 e4 Bf5 exf5 | 4.51 | none |
| Bird | Your hybrid | f4 d6 e4 e6 d4 Nf6 Nc3 | 0.72 | none |
| Bird | Pirc-like | f4 d6 e4 Nf6 Nc3 g6 d4 | 0.66 | none |
| Bird | French-like | f4 e6 e4 d5 d3 Nf6 e5 | 0.27 | none |
| Bird | Caro-like | f4 c6 e4 d5 d3 Bf5 exf5 | 3.78 | none |
| Larsen | Your hybrid | b3 d6 Bb2 e6 g3 Nf6 Bg2 | 0.46 | none |
| Larsen | Pirc-like | b3 d6 Bb2 Nf6 d4 g6 Nf3 | 0.15 | none |
| Larsen | French-like | b3 e6 g3 d5 Nf3 Nf6 Bg2 | 0.04 | none |
| Larsen | Caro-like | b3 c6 Bb2 d5 e3 Bf5 g4 | 0.32 | none |
| Nimzo-Larsen | Your hybrid | Nc3 d6 d4 e6 e4 Nf6 Nf3 | 0.76 | none |
| Nimzo-Larsen | Pirc-like | Nc3 d6 d4 Nf6 e4 g6 Be3 | 0.8 | none |
| Nimzo-Larsen | French-like | Nc3 e6 e4 d5 d4 Nf6 e5 | 0.42 | none |
| Nimzo-Larsen | Caro-like | Nc3 c6 Nf3 d5 e4 Bf5 exf5 | 4.37 | none |
| King fianchetto | Your hybrid | g3 d6 d4 e6 c4 Nf6 Nf3 | 0.69 | none |
| King fianchetto | Pirc-like | g3 d6 Nf3 Nf6 Bg2 g6 c4 | 0.5 | none |
| King fianchetto | French-like | g3 e6 Bg2 d5 Nf3 Nf6 d4 | 0.37 | none |
| King fianchetto | Caro-like | g3 c6 Bg2 d5 d4 Bf5 c4 | -0.08 | none |
| Sokolsky | Your hybrid | b4 d6 c4 e6 Nf3 Nf6 e3 | 0.16 | none |
| Sokolsky | Pirc-like | b4 d6 c4 Nf6 Bb2 g6 g3 | 0.25 | none |
| Sokolsky | French-like | b4 e6 a3 d5 e3 Nf6 Nf3 | -0.18 | none |
| Sokolsky | Caro-like | b4 c6 e3 d5 Bb2 Bf5 a3 | 0.0 | none |
| Van Geet flank | Your hybrid | a3 d6 d4 e6 e4 Nf6 Nc3 | 0.66 | none |
| Van Geet flank | Pirc-like | a3 d6 d4 Nf6 Nf3 g6 Nc3 | 0.31 | none |
| Van Geet flank | French-like | a3 e6 Nf3 d5 d4 Nf6 c4 | 0.06 | none |
| Van Geet flank | Caro-like | a3 c6 d4 d5 Nf3 Bf5 Bf4 | 0.22 | none |
| King-side pawn | Your hybrid | h3 d6 d4 e6 c4 Nf6 Nc3 | 0.39 | none |
| King-side pawn | Pirc-like | h3 d6 Nf3 Nf6 d4 g6 c4 | 0.49 | none |
| King-side pawn | French-like | h3 e6 e4 d5 exd5 Nf6 dxe6 | 1.0 | none |
| King-side pawn | Caro-like | h3 c6 e4 d5 exd5 Bf5 dxc6 | 0.92 | none |
| Grob | Your hybrid | g4 d6 h3 e6 Nf3 Nf6 Bg2 | 0.2 | none |
| Grob | Pirc-like | g4 d6 h3 Nf6 d4 g6 Bg2 | 0.13 | none |
| Grob | French-like | g4 e6 d4 d5 Bf4 Nf6 e3 | -0.66 | none |
| Grob | Caro-like | g4 c6 d4 d5 h3 Bf5 gxf5 | 4.05 | none |
