from django.urls import path

from .views import LoginHistoryView, MeView

urlpatterns = [
    path("me/", MeView.as_view(), name="user-me"),
    path("me/login-history/", LoginHistoryView.as_view(), name="login-history"),
]
