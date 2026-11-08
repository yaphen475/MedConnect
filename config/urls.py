from django.urls import include, path


urlpatterns = [
    path("accounts/", include("apps.accounts.urls")),
    path("patients/", include("apps.patients.urls")),
    path("agenda/", include("apps.agenda.urls")),
    path("dossiers/", include("apps.dossiers.urls")),
    path("messaging/", include("apps.messaging.urls")),
    path("chatbot/", include("apps.chatbot.urls")),
]
