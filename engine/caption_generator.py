import json
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_caption(meta: dict) -> dict:
    """Ask ChatGPT for caption + hashtags based on loop metadata."""
    prompt = f"""
    Create a short, catchy Instagram caption (max 2 sentences) and 8–10 relevant hashtags.
    Theme: {meta.get('theme')}
    Mood: {meta.get('mood')}
    Keywords: {', '.join(meta.get('keywords', []))}
    The style should sound natural and conversion-friendly.
    Output JSON with keys: caption, hashtags (as list).
    """

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        response_format={"type": "json_object"},
    )

    # Updated to match the modern SDK (no .parsed anymore)
    raw = resp.choices[0].message.content
    try:
        return json.loads(raw)
    except Exception:
        print("⚠️  Could not parse caption JSON, using fallback.")
        return {
            "caption": "Golden light over a quiet city skyline — calm meets creativity.",
            "hashtags": [
                "#LoopLabs",
                "#AI",
                "#Visuals",
                "#Sunrise",
                "#Cinematic",
                "#Creative",
                "#Inspiration",
                "#Design",
            ],
        }
