from django.urls import path
from .views import LoginAPIView, UserProfileAPIView

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("profile/", UserProfileAPIView.as_view(), name="profile"),
]
