import os
from moviepy.editor import VideoFileClip


def create_thumbnail(video_path: str, thumb_path: str, t: float = 0.5):
    """Extract a thumbnail frame from the middle of the video."""
    if not os.path.exists(video_path):
        print(f"⚠️  Video not found: {video_path}")
        return

    try:
        clip = VideoFileClip(video_path)
        frame_time = min(t, clip.duration / 2)
        frame = clip.get_frame(frame_time)
        # Save the frame
        from PIL import Image
        img = Image.fromarray(frame)
        img.save(thumb_path)
        clip.close()
        print(f"🖼️  Thumbnail saved: {thumb_path}")
    except Exception as e:
        print(f"⚠️  Failed to create thumbnail: {e}")
