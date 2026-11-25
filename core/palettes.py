PALETTES: dict[str, str] = {
    "standard": "@%#*+=-:. ",
    "detailed": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "blocks": "█▓▒░ ",
    "matrix": "01 ",
    "minimal": "#+. ",
}


def get_palette(style: str = "standard", invert: bool = False) -> str:
    """Return a brightness-ordered character ramp (darkest to lightest)."""
    if style not in PALETTES:
        valid_styles = ", ".join(PALETTES.keys())
        raise ValueError(f"Unknown style '{style}'. Choose from: {valid_styles}")

    palette = PALETTES[style]
    return palette[::-1] if invert else palette