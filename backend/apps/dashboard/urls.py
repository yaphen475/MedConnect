from django.urls import path

from .views import KpiView

urlpatterns = [
    path("kpi/", KpiView.as_view(), name="dashboard-kpi"),
]
