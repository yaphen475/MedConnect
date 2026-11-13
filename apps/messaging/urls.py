from django.urls import path

from apps.messaging import views

app_name = "messaging"

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("compose/", views.compose, name="compose"),
    path("thread/<int:pk>/", views.thread, name="thread"),
    path("start/<int:pk>/", views.start_with, name="start"),
]
