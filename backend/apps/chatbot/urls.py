from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import AskView, DocumentViewSet

router = DefaultRouter()
router.register("documents", DocumentViewSet)

urlpatterns = router.urls + [
    path("ask/", AskView.as_view(), name="chatbot-ask"),
]
