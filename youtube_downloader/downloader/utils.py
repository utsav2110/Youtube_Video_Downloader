# Final code for mp3 and mp4 conversion

import yt_dlp
from django.core.cache import cache
import os  
from datetime import datetime

CACHE_KEY = "download_progress"

def download_video(url, audio_only=False):
    current_date = datetime.now().strftime("%Y%m%d")
    output_template = os.path.join(os.path.expanduser("~"), "Downloads", "%(title)s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "progress_hooks": [progress_hook],
        "postprocessor_args": [
            '-metadata', f'date={current_date}',
            '-metadata', f'creation_time={current_date}'
        ],
    }

    if audio_only:
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
        ydl_opts["outtmpl"] = output_template.replace(".%(ext)s", ".mp3")  # Ensure output ends with .mp3
    else:
        ydl_opts["format"] = "best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"Error during download: {str(e)}")

def progress_hook(d):
    if d["status"] == "downloading":
        percent = (d.get("downloaded_bytes", 0) / d.get("total_bytes", 1)) * 100
        cache.set(CACHE_KEY, percent, timeout=60)
    elif d["status"] == "finished":
        cache.set(CACHE_KEY, 100, timeout=60)

