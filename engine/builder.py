import os, json, sys
from config import OUTPUT_ROOT
from utils.timestamp import now_id, now_readable
from utils.io_utils import ensure_dir, write_json
from generate_loop import get_visual_concept, build_loop
from caption_generator import generate_caption
from style_loader import load_style
from thumbnail import create_thumbnail

def main():
    if len(sys.argv) < 3:
        print("Usage: python builder.py '<prompt>' <style>")
        sys.exit(1)

    user_prompt = sys.argv[1]
    style_name = sys.argv[2]

    session_id = now_id()
    out_dir = ensure_dir(os.path.join(OUTPUT_ROOT, f"pack_{session_id}"))

    # --- STEP 1: Get concept and style ---
    meta = get_visual_concept(user_prompt)
    style = load_style(style_name)

    # Merge style attributes but don’t overwrite concept essentials
    for k, v in style.items():
        if k not in meta:
            meta[k] = v

    print(f"\n[LoopLabs] Building marketing pack ({style_name}) in {out_dir}...")
    print(f" - Text: {meta.get('text')}")
    print(f" - Mood: {meta.get('mood')}")
    print(f" - Motion: {meta.get('motion')}")
    print(f" - Palette: {meta.get('color')}  /  {meta.get('color_primary')}")
    print(f" - Font: {meta.get('font')}")
    print(f" - Music: {meta.get('music')}\n")

    # --- STEP 2: Build video ---
    video_path = os.path.join(out_dir, "loop.mp4")
    build_loop(meta, video_path)  # we'll enhance this later for bg audio

    # --- STEP 3: Thumbnail ---
    create_thumbnail(video_path, os.path.join(out_dir, "thumbnail.png"))

    # --- STEP 4: Captions ---
    cap = generate_caption(meta)
    caption_text = cap["caption"]
    hashtags_text = " ".join(cap["hashtags"])

    with open(os.path.join(out_dir, "caption.txt"), "w") as f:
        f.write(caption_text)
    with open(os.path.join(out_dir, "hashtags.txt"), "w") as f:
        f.write(hashtags_text)

    # --- STEP 5: Manifest ---
    manifest = {
        "prompt": user_prompt,
        "style": style_name,
        "mood": meta.get("mood"),
        "font": meta.get("font"),
        "music": meta.get("music"),
        "created": now_readable(),
        "assets": {
            "video": "loop.mp4",
            "thumbnail": "thumbnail.png",
            "caption": "caption.txt",
            "hashtags": "hashtags.txt",
        },
    }
    write_json(os.path.join(out_dir, "package_manifest.json"), manifest)

    print("\n✅ Marketing pack ready!")
    print(f"Video: {video_path}")
    print(f"Caption: {os.path.join(out_dir, 'caption.txt')}")

if __name__ == "__main__":
    main()
