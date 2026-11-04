from rest_framework.routers import DefaultRouter

from .views import AppointmentViewSet, AvailabilitySlotViewSet, BlockViewSet

router = DefaultRouter()
router.register("rendez-vous", AppointmentViewSet)
router.register("disponibilites", AvailabilitySlotViewSet)
router.register("indisponibilites", BlockViewSet)

urlpatterns = router.urls
