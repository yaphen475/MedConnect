from rest_framework.routers import DefaultRouter

from .views import CompteRenduViewSet, OrdonnanceViewSet

router = DefaultRouter()
router.register("comptes-rendus", CompteRenduViewSet)
router.register("ordonnances", OrdonnanceViewSet)

urlpatterns = router.urls
