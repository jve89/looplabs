# engine/main.py
"""
LoopLabs Engine v0.1
Stable build using MoviePy 1.0.3
"""

from moviepy.editor import TextClip, ColorClip, CompositeVideoClip
from pathlib import Path
import datetime


OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_clip(text: str, duration: int = 5, size=(720, 1280)):
    """Generate a simple branded clip with text overlay."""
    w, h = size
    bg = ColorClip(size, color=(20, 20, 20), duration=duration)

    txt = TextClip(
        txt=text,
        fontsize=48,
        color="white",
        font="Helvetica-Bold",
        size=(w - 100, None),
        method="caption",
    ).set_position("center").set_duration(duration)

    clip = CompositeVideoClip([bg, txt])

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"looplabs_{ts}.mp4"
    clip.write_videofile(str(output_path), fps=24, codec="libx264", audio=False)

    print(f"\n✅ Video generated: {output_path}")


if __name__ == "__main__":
    user_text = input("Enter your text: ").strip()
    if user_text:
        generate_clip(user_text)
    else:
        print("No text entered. Exiting.")
