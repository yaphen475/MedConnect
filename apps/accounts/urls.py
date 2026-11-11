from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from apps.accounts.views import dashboard, home


app_name = "accounts"

urlpatterns = [
    path("", home, name="home"),
    path(
        "login/",
        LoginView.as_view(
            template_name="accounts/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
]
