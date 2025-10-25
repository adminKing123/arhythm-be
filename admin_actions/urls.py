from django.urls import path
from .views import DownloadDBView, UpdateFromPreprodSSEView

urlpatterns = [
    path('download-db/', DownloadDBView.as_view(), name='download-db'),
    path('update-db-from-preprod/', UpdateFromPreprodSSEView.as_view(), name='update-db-from-preprod'),
]
