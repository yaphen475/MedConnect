from django.urls import path

from apps.chatbot import views

app_name = "chatbot"

urlpatterns = [
    path("", views.chat, name="chat"),
    path("clear/", views.clear, name="clear"),
]
