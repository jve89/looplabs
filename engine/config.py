import os
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(dotenv_path=os.path.join(ROOT_DIR, ".env"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OUTPUT_ROOT = os.path.join(os.getcwd(), "output")
VIDEO_RES = (720, 720)
FPS = 24
DURATION = 5
MODEL = "gpt-4o-mini"  # fast & affordable
