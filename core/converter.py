import cv2
import numpy as np
from core.palettes import get_palette


def resize_frame(frame: np.ndarray, width: int, aspect_ratio: float = 0.5) -> np.ndarray:
    """Resize frame to target character width while correcting terminal character height."""
    orig_h, orig_w = frame.shape[:2]
    new_height = max(1, int(width * (orig_h / orig_w) * aspect_ratio))
    return cv2.resize(frame, (width, new_height), interpolation=cv2.INTER_AREA)


def detect_edges(
    frame: np.ndarray, low_threshold: int = 80, high_threshold: int = 160
) -> np.ndarray:
    """Convert frame to a high-contrast Canny edge map."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    return cv2.Canny(blurred, low_threshold, high_threshold)


def map_pixels_to_chars(gray_frame: np.ndarray, palette: str) -> list[str]:
    """Map 0-255 grayscale pixel values to ASCII characters using NumPy indexing."""
    num_chars = len(palette)
    indices = (gray_frame.astype(np.float32) / 256.0 * num_chars).astype(np.int32)
    indices = np.clip(indices, 0, num_chars - 1)

    palette_arr = np.array(list(palette))
    char_grid = palette_arr[indices]
    return ["".join(row) for row in char_grid]


def apply_ansi_color(ascii_lines: list[str], bgr_frame: np.ndarray) -> str:
    """Wrap each ASCII character in 24-bit ANSI RGB color codes."""
    colored_lines = []
    for line, bgr_row in zip(ascii_lines, bgr_frame):
        colored_chars = [
            f"\033[38;2;{r};{g};{b}m{char}"
            for char, (b, g, r) in zip(line, bgr_row)
        ]
        colored_lines.append("".join(colored_chars) + "\033[0m")
    return "\n".join(colored_lines)


def frame_to_ascii(
    frame: np.ndarray,
    width: int = 100,
    style: str = "standard",
    invert: bool = True,
    color: bool = False,
    edge_mode: bool = False,
) -> str:
    """Convert a BGR OpenCV frame into a formatted ASCII art string."""
    resized = resize_frame(frame, width=width)

    if edge_mode:
        processed = detect_edges(resized)
    else:
        processed = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    palette = get_palette(style=style, invert=invert)
    ascii_lines = map_pixels_to_chars(processed, palette)

    if color:
        return apply_ansi_color(ascii_lines, resized)
    return "\n".join(ascii_lines)