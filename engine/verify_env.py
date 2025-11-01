import sys, subprocess, os
from moviepy.editor import ColorClip

print(f"Python {sys.version.split()[0]} OK")
subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.DEVNULL)
clip = ColorClip((64, 64), color=(255, 0, 0), duration=0.5)
clip.write_videofile("verify_test.mp4", fps=24, logger=None)
os.remove("verify_test.mp4")
print("MoviePy + FFmpeg OK — test passed.")
