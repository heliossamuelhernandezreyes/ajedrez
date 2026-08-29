# Ajedrez — Texcatlipocatl Chess Lab

Repositorio para guardar y analizar partidas de ajedrez con Stockfish mediante GitHub Actions.

## Estructura

- `games/`: partidas PGN.
- `analysis/`: resultados generados automáticamente en Markdown y JSON.
- `analyze.py`: analizador con Stockfish.
- `.github/workflows/chess-lab.yml`: automatización.

Al añadir un PGN a `games/`, GitHub Actions ejecuta Stockfish (profundidad 20, MultiPV 3) y guarda el análisis en `analysis/`.
