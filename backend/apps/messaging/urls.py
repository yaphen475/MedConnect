from rest_framework.routers import DefaultRouter

from .views import MessageViewSet, ThreadViewSet

router = DefaultRouter()
router.register("threads", ThreadViewSet)
router.register("messages", MessageViewSet)

urlpatterns = router.urls
