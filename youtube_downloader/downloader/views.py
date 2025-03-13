import time
from django.http import JsonResponse
from django.shortcuts import render
from django.core.cache import cache
from .utils import download_video
import threading
import yt_dlp

CACHE_KEY = "download_progress"


def download_page(request):
    if request.method == "POST":
        url = request.POST.get("url")
        audio_only = True if request.POST.get("audio_only") == "on" else False

        if url:
            t = threading.Thread(target=download_video, args=(url, audio_only))
            t.start()
            return JsonResponse({"message": "Download started!"})

    return render(request, "downloader/download.html")


def get_progress(request):
    progress = cache.get(CACHE_KEY, 0)
    return JsonResponse({"progress": progress})


def get_video_details(request):
    url = request.GET.get("url")
    if url:
        try:
            ydl_opts = {"quiet": True, "skip_download": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            return JsonResponse(
                {
                    "thumbnail": info.get("thumbnail", ""),
                    "description": info.get("description", ""),
                }
            )
        except Exception as e:
            return JsonResponse({"error": str(e)})
    return JsonResponse({"error": "No URL provided"})
