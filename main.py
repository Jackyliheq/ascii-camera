import argparse
import os
import sys
import time

from core.converter import frame_to_ascii
from core.palettes import PALETTES
from core.renderer import (
    init_terminal,
    poll_keypress,
    render_frame,
    restore_terminal,
    save_snapshot,
)
from core.sources import load_image, stream_webcam


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for image or webcam ASCII conversion."""
    parser = argparse.ArgumentParser(
        description="Convert images or live webcam video into terminal ASCII art."
    )

    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--image", type=str, help="Path to a static image file (e.g., assets/photo.jpg)"
    )
    source_group.add_argument(
        "--webcam", action="store_true", help="Stream live video from your webcam"
    )

    parser.add_argument(
        "--width", type=int, default=100, help="Output width in characters (default: 100)"
    )
    parser.add_argument(
        "--style",
        type=str,
        default="standard",
        choices=list(PALETTES.keys()),
        help="Character palette preset (default: standard)",
    )
    parser.add_argument(
        "--color", action="store_true", help="Enable 24-bit ANSI RGB terminal colors"
    )
    parser.add_argument(
        "--no-invert",
        action="store_true",
        help="Disable brightness inversion (best for light-background terminals)",
    )
    parser.add_argument(
        "--edges", action="store_true", help="Enable Canny edge-detection sketch mode"
    )
    parser.add_argument(
        "--save", action="store_true", help="Save output to the outputs/ folder"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Export snapshots as styled .html instead of .txt",
    )
    parser.add_argument(
        "--camera", type=int, default=0, help="Webcam device index (default: 0)"
    )
    parser.add_argument(
        "--fps", type=int, default=30, help="Target FPS cap in webcam mode (default: 30)"
    )

    return parser.parse_args()


def run_image_mode(args: argparse.Namespace) -> None:
    """Convert and print a single image file, optionally saving a snapshot."""
    if os.name == "nt" and args.color:
        os.system("")

    frame = load_image(args.image)
    ascii_art = frame_to_ascii(
        frame=frame,
        width=args.width,
        style=args.style,
        invert=not args.no_invert,
        color=args.color,
        edge_mode=args.edges,
    )
    print(ascii_art)

    if args.save or args.html:
        saved_path = save_snapshot(ascii_art, as_html=args.html)
        print(f"\nSaved snapshot to: {saved_path}")


def run_webcam_mode(args: argparse.Namespace) -> None:
    """Stream webcam frames to the terminal with live keyboard controls."""
    styles = list(PALETTES.keys())
    style_idx = styles.index(args.style)
    width = max(20, min(240, args.width))
    color = args.color
    invert = not args.no_invert
    edge_mode = args.edges

    frame_delay = 1.0 / max(1, args.fps)
    notice = ""
    notice_until = 0.0

    init_terminal()
    try:
        for frame in stream_webcam(camera_index=args.camera, mirror=True):
            loop_start = time.perf_counter()

            key = poll_keypress()
            if key == "q":
                break
            elif key == "c":
                color = not color
            elif key == "i":
                invert = not invert
            elif key == "e":
                edge_mode = not edge_mode
            elif key == "p":
                style_idx = (style_idx + 1) % len(styles)
            elif key in ("+", "="):
                width = min(240, width + 10)
            elif key in ("-", "_"):
                width = max(20, width - 10)
                sys.stdout.write("\033[2J")
            elif key == "s":
                preview_art = frame_to_ascii(
                    frame=frame,
                    width=width,
                    style=styles[style_idx],
                    invert=invert,
                    color=color,
                    edge_mode=edge_mode,
                )
                saved_path = save_snapshot(preview_art, as_html=args.html)
                notice = f" | Saved: {saved_path}"
                notice_until = time.perf_counter() + 2.5

            ascii_art = frame_to_ascii(
                frame=frame,
                width=width,
                style=styles[style_idx],
                invert=invert,
                color=color,
                edge_mode=edge_mode,
            )

            elapsed = time.perf_counter() - loop_start
            if elapsed < frame_delay:
                time.sleep(frame_delay - elapsed)

            actual_fps = 1.0 / max(1e-6, time.perf_counter() - loop_start)
            active_notice = notice if time.perf_counter() < notice_until else ""
            status_bar = (
                f"[{styles[style_idx]} | W:{width} | Color:{'ON' if color else 'OFF'} | "
                f"Edges:{'ON' if edge_mode else 'OFF'} | {actual_fps:.0f} FPS]  "
                f"Keys: [C]olor [E]dges [I]nvert [P]alette [+/-]Size [S]ave [Q]uit"
                f"{active_notice}"
            )
            render_frame(ascii_art, status_bar=status_bar)
    finally:
        restore_terminal()


def main() -> None:
    """Application entry point."""
    args = parse_args()
    try:
        if args.image:
            run_image_mode(args)
        elif args.webcam:
            run_webcam_mode(args)
    except KeyboardInterrupt:
        pass
    except (FileNotFoundError, ValueError, RuntimeError) as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()