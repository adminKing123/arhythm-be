from django.urls import path
from .views import DownloadDBView

urlpatterns = [
    path('download-db/', DownloadDBView.as_view(), name='download-db'),
]
