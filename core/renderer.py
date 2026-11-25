from datetime import datetime
import html
import os
import re
import sys

if os.name == "nt":
    import msvcrt
else:
    import select
    import termios
    import tty

ANSI_ESCAPE_RE = re.compile(r"\033\[[0-9;]*m")
ANSI_RGB_CHAR_RE = re.compile(r"\033\[38;2;(\d+);(\d+);(\d+)m(.)")

_posix_old_settings = None


def init_terminal() -> None:
    """Enable ANSI escape codes, hide the cursor, and clear the screen once."""
    global _posix_old_settings
    if os.name == "nt":
        os.system("")
    elif sys.stdin.isatty():
        _posix_old_settings = termios.tcgetattr(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())

    sys.stdout.write("\033[?25l\033[2J\033[H")
    sys.stdout.flush()


def restore_terminal() -> None:
    """Restore terminal input settings, formatting, and visible cursor."""
    global _posix_old_settings
    if os.name != "nt" and _posix_old_settings is not None:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _posix_old_settings)
        _posix_old_settings = None

    sys.stdout.write("\033[0m\033[?25h\n")
    sys.stdout.flush()


def render_frame(ascii_art: str, status_bar: str = "") -> None:
    """Move cursor to top-left and overwrite the terminal frame without flickering."""
    output = f"\033[H{ascii_art}"
    if status_bar:
        output += f"\n\033[0m{status_bar}\033[K"
    sys.stdout.write(output)
    sys.stdout.flush()


def poll_keypress() -> str | None:
    """Read a single keypress without blocking the render loop."""
    if os.name == "nt":
        if msvcrt.kbhit():
            key = msvcrt.getwch()
            if key in ("\x00", "\xe0"):
                msvcrt.getwch()
                return None
            return key.lower()
        return None

    if sys.stdin.isatty():
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        if ready:
            return sys.stdin.read(1).lower()
    return None


def _ansi_to_html(ascii_art: str) -> str:
    """Convert 24-bit ANSI colored ASCII text into escaped HTML spans."""
    if "\033[38;2;" not in ascii_art:
        return html.escape(ascii_art)

    cleaned = ascii_art.replace("\033[0m", "")
    return ANSI_RGB_CHAR_RE.sub(
        lambda m: (
            f'<span style="color:rgb({m.group(1)},{m.group(2)},{m.group(3)})">'
            f"{html.escape(m.group(4))}</span>"
        ),
        cleaned,
    )


def save_snapshot(
    ascii_art: str, output_dir: str = "outputs", as_html: bool = False
) -> str:
    """Save an ASCII frame to a timestamped .txt or .html file and return its path."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if as_html:
        file_path = os.path.join(output_dir, f"ascii_{timestamp}.html")
        body = _ansi_to_html(ascii_art)
        document = (
            "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"UTF-8\">\n"
            "<title>ASCII Snapshot</title>\n<style>\n"
            "body { background: #0d1117; color: #e6edf3; display: flex; "
            "justify-content: center; padding: 24px; margin: 0; }\n"
            "pre { font-family: 'Courier New', Consolas, monospace; "
            "font-size: 10px; line-height: 1.0; letter-spacing: 0; }\n"
            "</style>\n</head>\n<body>\n"
            f"<pre>{body}</pre>\n"
            "</body>\n</html>\n"
        )
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(document)
        return file_path

    file_path = os.path.join(output_dir, f"ascii_{timestamp}.txt")
    plain_text = ANSI_ESCAPE_RE.sub("", ascii_art)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(plain_text + "\n")
    return file_path