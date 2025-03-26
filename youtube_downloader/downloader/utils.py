import yt_dlp
from django.core.cache import cache
import os
import time
from datetime import datetime
import re

CACHE_KEY = "download_progress"

def sanitize_filename(title):
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', title)
    sanitized = re.sub(r'_+', '_', sanitized)
    sanitized = sanitized.strip('. ')
    sanitized = sanitized[:200]
    return sanitized if sanitized else 'video'

def download_video(url, audio_only=False, session_key=None):
    current_date = datetime.now().strftime("%Y%m%d")
    temp_dir = os.path.join(os.path.expanduser("~"), "Downloads", ".temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Use temp directory for initial download
    output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "progress_hooks": [progress_hook],
    }

    if audio_only:
        ydl_opts["format"] = "bestaudio[ext=webm]"
        ydl_opts["outtmpl"] = output_template.replace(".%(ext)s", ".webm")
    else:
        ydl_opts["format"] = "best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
        title = info.get("title", "video")
        safe_title = sanitize_filename(title)
        ext = "webm" if audio_only else "mp4"
        
        # Get the path of the downloaded file
        downloaded_file = os.path.join(temp_dir, f"{safe_title}.{ext}")
        
        # Store the file path in cache with session key
        if session_key:
            cache.set(f"download_path_{session_key}", downloaded_file, timeout=300)
        
        return downloaded_file
        
    except Exception as e:
        print(f"Error during download: {str(e)}")
        return None

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