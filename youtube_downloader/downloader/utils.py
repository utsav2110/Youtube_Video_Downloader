import yt_dlp
from django.core.cache import cache
import os
import time
from datetime import datetime

CACHE_KEY = "download_progress"

def download_video(url, audio_only=False):
    current_date = datetime.now().strftime("%Y%m%d")
    output_template = os.path.join(os.path.expanduser("~"), "Downloads", "%(title)s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "progress_hooks": [progress_hook],
    }

    if audio_only:
        ydl_opts["format"] = "bestaudio[ext=webm]"  # Use WEBM instead of MP3
        ydl_opts["outtmpl"] = output_template.replace(".%(ext)s", ".webm")  # Ensure WEBM extension
    else:
        ydl_opts["format"] = "best"

    # Extract video info to compute filename.
    with yt_dlp.YoutubeDL({}) as ydl_temp:
        info = ydl_temp.extract_info(url, download=False)
    title = info.get("title", "video")

    # Determine extension and download directory.
    download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    ext = "webm" if audio_only else "mp4"  # Change extension based on type

    # Build candidate filename and increment suffix if already exists.
    candidate = os.path.join(download_dir, f"{title}.{ext}")
    count = 0
    while os.path.exists(candidate):
        count += 1
        candidate = os.path.join(download_dir, f"{title}{count}.{ext}")
    ydl_opts["outtmpl"] = candidate

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        update_file_timestamp(candidate)
        
    except Exception as e:
        print(f"Error during download: {str(e)}")

def progress_hook(d):
    if d["status"] == "downloading":
        percent = (d.get("downloaded_bytes", 0) / d.get("total_bytes", 1)) * 100
        cache.set(CACHE_KEY, percent, timeout=60)
    elif d["status"] == "finished":
        cache.set(CACHE_KEY, 100, timeout=60)


def update_file_timestamp(file_path):
    """Change the file's modification, creation (Windows), and access time to the current date."""
    timestamp = time.time()  # Current timestamp

    try:
        # Update modification and access time (Linux/macOS/Windows)
        os.utime(file_path, (timestamp, timestamp))

        # Update creation time (Windows only)
        if os.name == "nt":
            import win32file, pywintypes
            file_handle = win32file.CreateFile(
                file_path,
                win32file.GENERIC_WRITE,
                win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE | win32file.FILE_SHARE_DELETE,
                None,
                win32file.OPEN_EXISTING,
                0,
                None,
            )
            new_time = pywintypes.Time(timestamp)
            win32file.SetFileTime(file_handle, new_time, new_time, new_time)
            file_handle.close()

        print(f"Timestamps updated for {file_path}")
    
    except Exception as e:
        print(f"Failed to update timestamps: {str(e)}")