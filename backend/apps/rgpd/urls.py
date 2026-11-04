from rest_framework.routers import DefaultRouter

from .views import ConsentementViewSet, DemandeDonneeViewSet, JournalAccesViewSet, RegleRetentionViewSet

router = DefaultRouter()
router.register("consentements", ConsentementViewSet)
router.register("demandes", DemandeDonneeViewSet)
router.register("journal", JournalAccesViewSet)
router.register("retention", RegleRetentionViewSet)

urlpatterns = router.urls
