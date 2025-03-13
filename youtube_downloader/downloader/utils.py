import yt_dlp
from django.core.cache import cache
import os  

CACHE_KEY = "download_progress"


def download_video(url, audio_only=False):
    ydl_opts = {
        "outtmpl": os.path.join(
            os.path.expanduser("~"), "Downloads", "%(title)s.%(ext)s"
        ), 
        "progress_hooks": [progress_hook],
    }
    if audio_only:
        ydl_opts["format"] = "bestaudio"
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ]
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
