import os, sys, random, json
from openai import OpenAI
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
from config import OPENAI_API_KEY, OUTPUT_ROOT, VIDEO_RES, FPS, DURATION, MODEL
from utils.timestamp import now_id, now_readable
from utils.io_utils import ensure_dir, write_text, write_json
from caption_generator import generate_caption

client = OpenAI(api_key=OPENAI_API_KEY)


def get_visual_concept(prompt: str) -> dict:
    """Ask ChatGPT for color/motion/text concept for the loop."""
    query = f"""
    Turn this idea into simple visual parameters for a short looping video.
    Prompt: "{prompt}"
    Reply in JSON with keys:
    color (RGB list 0-255),
    text (short overlay),
    mood (string),
    motion ('pulse', 'fade', or 'none'),
    keywords (array of 3–5 words),
    theme (1-2 words summary).
    Keep it minimal, cinematic, and brand-friendly.
    """

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": query}],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    # the new SDK exposes the JSON as .message.content, not .parsed
    raw = resp.choices[0].message.content
    try:
        return json.loads(raw)
    except Exception:
        print("⚠️  Could not parse JSON, using fallback.")
        return {"color": [0, 0, 255], "text": "LoopLabs", "motion": "none", "mood": "neutral"}


def build_loop(meta: dict, out_path: str):
    """Generate simple looping animation with MoviePy."""
    color = meta.get("color", [0, 0, 0])
    base = ColorClip(VIDEO_RES, color=color, duration=DURATION)

    # Simple motion
    if meta.get("motion") == "pulse":
        def fl(gf, t):
            return gf(t) * (0.5 + 0.5 * abs(random.random()))
        base = base.fl(fl)
    elif meta.get("motion") == "fade":
        base = base.crossfadein(1).crossfadeout(1)

    txt = meta.get("text", "")
    if txt:
        text_clip = TextClip(
            txt, fontsize=60, color="white", font="Helvetica-Bold"
        ).set_position("center").set_duration(DURATION)
        final = CompositeVideoClip([base, text_clip])
    else:
        final = base

    final.write_videofile(out_path, fps=FPS, codec="libx264", audio=False)


def main():
    if len(sys.argv) < 2:
        print('Usage: python generate_loop.py "your prompt here"')
        sys.exit(1)

    user_prompt = sys.argv[1]
    meta = get_visual_concept(user_prompt)
    cap = generate_caption(meta)

    session_id = now_id()
    out_dir = ensure_dir(os.path.join(OUTPUT_ROOT, f"loop_{session_id}"))
    video_path = os.path.join(out_dir, "loop.mp4")

    print(f"\n[LoopLabs] Creating video in {out_dir}...\n")
    build_loop(meta, video_path)

    caption_text = f"{cap['caption']}\n\n{' '.join(cap['hashtags'])}"
    write_text(os.path.join(out_dir, "caption.txt"), caption_text)
    write_json(
        os.path.join(out_dir, "metadata.json"),
        {**meta, **cap, "created": now_readable()},
    )

    print("\n✅ LoopLabs content pack ready!")
    print(f"Video: {video_path}")
    print(f"Caption: {os.path.join(out_dir, 'caption.txt')}")


if __name__ == "__main__":
    main()
