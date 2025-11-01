import os, json

STYLE_DIR = os.path.join(os.path.dirname(__file__), "styles")

# --- Built-in fallback presets ---
DEFAULT_STYLES = {
    "minimalist": {
        "color_primary": [255, 255, 255],
        "text_color": "white",
        "font": "Helvetica-Bold",
        "font_size": 60,
        "music": "assets/audio/chill.mp3",
    },
    "luxury": {
        "color_primary": [30, 30, 30],
        "text_color": "#f5d742",
        "font": "Times-Bold",
        "font_size": 70,
        "music": "assets/audio/corporate.mp3",
    },
    "energetic": {
        "color_primary": [255, 80, 80],
        "text_color": "white",
        "font": "Arial-Bold",
        "font_size": 65,
        "music": "assets/audio/energetic.mp3",
    },
}


def load_style(name: str) -> dict:
    """Load a style preset from /engine/styles or fall back to defaults."""
    name = name.lower().strip()
    path = os.path.join(STYLE_DIR, f"{name}.json")

    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Failed to load {path}: {e}")
    elif name in DEFAULT_STYLES:
        return DEFAULT_STYLES[name]

    print(f"⚠️  Unknown style '{name}', using minimalist fallback.")
    return DEFAULT_STYLES["minimalist"]
