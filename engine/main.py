# engine/main.py
"""
LoopLabs Engine v0.3
Handles JSON input and delegates generation to generator.py
"""

import sys
import json
from pathlib import Path
from generator import generate_clip


def main():
    # Read raw input from stdin
    raw_input = sys.stdin.read().strip()
    if not raw_input:
        print("❌ No input received.")
        sys.exit(1)

    # Try to parse JSON input from API
    try:
        data = json.loads(raw_input)
    except json.JSONDecodeError:
        data = {"text": raw_input}

    text = data.get("text") or data.get("prompt") or "Default text"
    duration = int(data.get("duration", 5))
    theme = data.get("theme", "dark")
    font = data.get("font", "Helvetica-Bold")
    logo = data.get("logo", "assets/logo.png")

    print(f"🎬 Generating video: text='{text}' theme='{theme}' duration={duration}s")

    output_path = generate_clip(
        text=text,
        duration=duration,
        theme=theme,
        font=font,
        logo_path=Path(logo) if logo else None,
    )

    print(f"\n✅ Video generated: {output_path}")


if __name__ == "__main__":
    main()
