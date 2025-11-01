"""
LoopLabs Engine – generator module
Handles all rendering logic, colors, motion, and optional background music.
"""

from moviepy.editor import (
    TextClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    AudioFileClip,
)
from pathlib import Path
from typing import Optional
import datetime

# --- Directories ---
ENGINE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ENGINE_DIR.parent / "output"
ASSETS_DIR = ENGINE_DIR.parent / "assets" / "audio"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def generate_clip(
    text: str,
    duration: int = 5,
    size=(720, 1280),
    theme: str = "dark",
    font: str = "Helvetica-Bold",
    logo_path: Optional[Path] = None,
    audio_name: Optional[str] = None,
):
    """Generate a motion clip with background, text, optional logo, and music."""
    w, h = size

    # --- Color themes ---
    themes = {
        "dark": (20, 20, 20),
        "light": (240, 240, 240),
        "blue": (30, 60, 120),
        "sunset": (255, 94, 77),
    }
    bg_color = themes.get(theme, (20, 20, 20))

    # --- Background ---
    bg = ColorClip(size, color=bg_color, duration=duration)

    # --- Text layer ---
    txt_color = "black" if theme == "light" else "white"
    txt = (
        TextClip(
            txt=text,
            fontsize=54,
            color=txt_color,
            font=font,
            size=(w - 100, None),
            method="caption",
        )
        .set_position("center")
        .set_duration(duration)
        .crossfadein(1.0)
    )

    clips = [bg, txt]

    # --- Optional logo overlay ---
    if logo_path and logo_path.exists():
        logo = (
            ImageClip(str(logo_path))
            .set_duration(duration)
            .resize(width=120)
            .set_position(("right", "top"))
            .crossfadein(0.5)
        )
        clips.append(logo)

    # --- Merge visuals ---
    final = CompositeVideoClip(clips)

    # --- Optional audio ---
    if audio_name:
        audio_file = ASSETS_DIR / f"{audio_name}.mp3"
        if audio_file.exists():
            music = AudioFileClip(str(audio_file)).subclip(0, duration)
            final = final.set_audio(music)
        else:
            print(f"⚠️  Audio file not found: {audio_file}")

    # --- Output video ---
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"looplabs_{theme}_{ts}.mp4"
    final.write_videofile(str(output_path), fps=24, codec="libx264", audio=True)

    return output_path
