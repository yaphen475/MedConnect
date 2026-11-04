from rest_framework.routers import DefaultRouter

from .views import PatientScoreViewSet, SegmentAssignmentViewSet, SegmentViewSet

router = DefaultRouter()
router.register("segments", SegmentViewSet)
router.register("affectations", SegmentAssignmentViewSet)
router.register("scores", PatientScoreViewSet)

urlpatterns = router.urls
