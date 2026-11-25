import cv2
import numpy as np

WINDOW_NAME = "ASCII Cam"
_GLYPH_CACHE: dict[tuple[str, int, int], dict[str, np.ndarray]] = {}


def _get_glyph_masks(
    charset: str, cell_w: int, cell_h: int
) -> dict[str, np.ndarray]:
    """Pre-render boolean character masks once per unique character set."""
    cache_key = (charset, cell_w, cell_h)
    if cache_key in _GLYPH_CACHE:
        return _GLYPH_CACHE[cache_key]

    masks: dict[str, np.ndarray] = {}
    for ch in set(charset):
        if ch == " ":
            continue
        tile = np.zeros((cell_h, cell_w), dtype=np.uint8)
        cv2.putText(
            tile,
            ch,
            (1, cell_h - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            255,
            1,
            cv2.LINE_AA,
        )
        masks[ch] = tile > 90

    _GLYPH_CACHE[cache_key] = masks
    return masks


def render_ascii_canvas(
    ascii_lines: list[str],
    bgr_frame: np.ndarray | None = None,
    invert: bool = True,
    status_bar: str = "",
    cell_w: int = 10,
    cell_h: int = 18,
) -> np.ndarray:
    """Draw ASCII characters onto a fixed-grid NumPy image canvas."""
    rows = len(ascii_lines)
    cols = len(ascii_lines[0]) if rows > 0 else 0
    footer_h = 28 if status_bar else 0

    bg_color = (13, 17, 23) if invert else (245, 245, 245)
    default_fg = (230, 237, 243) if invert else (25, 25, 25)

    canvas = np.full(
        (rows * cell_h + footer_h, cols * cell_w, 3), bg_color, dtype=np.uint8
    )

    charset = "".join(ascii_lines)
    glyph_masks = _get_glyph_masks(charset, cell_w, cell_h)

    for r, line in enumerate(ascii_lines):
        y0 = r * cell_h
        y1 = y0 + cell_h
        for c, char in enumerate(line):
            if char == " ":
                continue

            mask = glyph_masks[char]
            x0 = c * cell_w
            x1 = x0 + cell_w

            if bgr_frame is not None:
                canvas[y0:y1, x0:x1][mask] = bgr_frame[r, c]
            else:
                canvas[y0:y1, x0:x1][mask] = default_fg

    if status_bar:
        cv2.putText(
            canvas,
            status_bar,
            (8, rows * cell_h + 19),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            default_fg,
            1,
            cv2.LINE_AA,
        )

    return canvas


def show_window(canvas: np.ndarray) -> bool:
    """Display the rendered canvas and return False if the user closed the window."""
    cv2.imshow(WINDOW_NAME, canvas)
    return cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) >= 1


def poll_window_key() -> str | None:
    """Read a keypress from the active OpenCV window without blocking."""
    key_code = cv2.waitKey(1) & 0xFF
    if key_code == 255:
        return None
    return chr(key_code).lower()


def close_window() -> None:
    """Destroy all OpenCV GUI windows."""
    cv2.destroyAllWindows()