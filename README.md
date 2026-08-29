# Ajedrez — Texcatlipocatl Chess Lab

Repositorio para guardar y analizar partidas de ajedrez con Stockfish mediante GitHub Actions.

## Motor

El laboratorio usa **Stockfish 18 oficial con NNUE**, descargado directamente desde la release oficial de Stockfish para Ubuntu x86-64 AVX2. El workflow verifica el SHA-256 del archivo antes de ejecutarlo.

Configuración de análisis por defecto:

- Profundidad: **20**
- MultiPV: **3**
- Motor: **Stockfish 18 NNUE**

## Estructura

- `games/`: partidas PGN.
- `analysis/`: resultados generados automáticamente en Markdown y JSON.
- `analyze.py`: analizador con Stockfish.
- `.github/workflows/chess-lab.yml`: automatización.

Al añadir un PGN a `games/`, GitHub Actions ejecuta Stockfish 18 NNUE y guarda el análisis en `analysis/`.
