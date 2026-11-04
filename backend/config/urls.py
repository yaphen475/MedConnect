from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok", "service": "microprojet-si"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/patients/", include("apps.patients.urls")),
    path("api/agenda/", include("apps.agenda.urls")),
    path("api/messagerie/", include("apps.messaging.urls")),
    path("api/segments/", include("apps.segments.urls")),
    path("api/rgpd/", include("apps.rgpd.urls")),
    path("api/dossiers/", include("apps.dossiers.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    path("api/chatbot/", include("apps.chatbot.urls")),
]
