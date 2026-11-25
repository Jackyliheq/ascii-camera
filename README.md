# ASCII Cam

A lightweight Python CLI tool that converts static images and live webcam feeds into real-time ASCII art—rendered directly in your terminal or in a dedicated OpenCV GUI window, complete with 24-bit colors, Canny edge-detection sketch mode, live keyboard controls, and `.txt`/`.html` snapshot exports.

## Features

- **Unified Image & Webcam Engine:** Processes static image files and live camera streams through the same vectorized NumPy pipeline.
- **Dual Display Modes:** Render flicker-free output directly inside your terminal (`\033[H`) or launch a separate desktop GUI window with `--window`.
- **Aspect-Ratio Compensation:** Automatically scales vertical resolution (`0.5x`) so monospace characters render with accurate proportions.
- **Multiple Character Palettes:** Switch between `standard`, `detailed`, `blocks`, `matrix`, and `minimal` character ramps, with brightness inversion for dark or light backgrounds.
- **RGB Color & Edge Modes:** Render full color output or Canny edge-detected outlines.
- **Live Keyboard Controls:** Toggle colors, edge detection, palettes, inversion, and resolution in real time without restarting the stream.
- **Text & HTML Snapshot Export:** Save any frame to `outputs/` as plain text (`.txt`) or a standalone dark-mode webpage (`.html`) preserving full RGB colors.

## Project Structure

```text
ascii-cam/
├── core/
│   ├── __init__.py       # Package initializer
│   ├── palettes.py       # Brightness-ordered character ramps
│   ├── converter.py      # Resizing, edge detection, and ASCII/ANSI mapping
│   ├── sources.py        # Static image loader and webcam frame generator
│   ├── renderer.py       # Flicker-free terminal output, key listener, and .txt/.html export
│   └── window.py         # Fixed-grid OpenCV GUI window renderer with glyph caching
├── assets/               # Sample input images
├── outputs/              # Saved .txt and .html ASCII snapshots
├── main.py               # CLI argument parser and execution loop
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Installation

1. Clone the repository and navigate into the project directory:
   ```bash
   git clone <your-repo-url>
   cd ascii-cam
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Static Image Mode
Convert an image file and print it to the terminal:
```bash
python main.py --image assets/sample.jpg --width 100
```

Render in full 24-bit color and save an `.html` snapshot to `outputs/`:
```bash
python main.py --image assets/sample.jpg --width 120 --color --html
```

### Live Webcam Mode (Terminal)
Start the real-time webcam ASCII stream inside your terminal:
```bash
python main.py --webcam --width 110
```

### Live Webcam Mode (GUI Window)
Open the webcam ASCII feed in a dedicated desktop window:
```bash
python main.py --webcam --window --width 90 --color
```

Launch directly in edge-detection sketch mode:
```bash
python main.py --webcam --window --edges --style detailed
```

## CLI Options

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--image PATH` | — | Path to an input image file (mutually exclusive with `--webcam`) |
| `--webcam` | — | Stream live video from your webcam (mutually exclusive with `--image`) |
| `--window` | `False` | Display webcam ASCII output in a separate GUI window instead of the terminal |
| `--width INT` | `100` | Output width in characters |
| `--style NAME` | `standard` | Character palette (`standard`, `detailed`, `blocks`, `matrix`, `minimal`) |
| `--color` | `False` | Enable RGB colors (24-bit ANSI in terminal, BGR pixel colors in GUI window) |
| `--no-invert` | `False