from django.urls import path
from .views import *

urlpatterns = [
    path('files/', FilesCreateGetApiViews.as_view()),
    path('files/<str:id>/', FileUpdateApiViews.as_view()),
    path('files/<str:id>/download/', FileDownloadViews.as_view()),
    path('files/<str:id>/<str:token>/view/', FileSharedDataViews.as_view()),
    path('files/<str:token>/post/', PostSharedFileData.as_view()),
    path('files/<str:id>/download/<str:token>/', FileDownloadsViews.as_view()),
    path('media-storage-size/', MediaStorageSizeView.as_view(), name='media-storage-size'),
    path('file/ocr/', FilesOcrApiViews.as_view()),
]