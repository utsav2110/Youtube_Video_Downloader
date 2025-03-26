from django.urls import path
from . import views

urlpatterns = [
    path('', views.download_page, name='download_page'),
    path('progress/', views.get_progress, name='get_progress'),
    path('video_details/', views.get_video_details, name='video_details'),
]
