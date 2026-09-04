from django.urls import path
from .views import DownloadDBView, DownloadDBJsonView

urlpatterns = [
    path('download-db/', DownloadDBView.as_view(), name='download-db'),
    path('db-to-json/', DownloadDBJsonView.as_view(), name='download-db'),
]
