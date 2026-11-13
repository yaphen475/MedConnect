from django.urls import path

from apps.dossiers import views

app_name = "dossiers"

urlpatterns = [
    path("new/", views.report_new, name="report_new"),
    path(
        "patient/<int:patient_id>/",
        views.patient_history,
        name="patient_history",
    ),
    path("reports/<int:pk>/delete/", views.report_delete, name="report_delete"),
    path("prescriptions/new/", views.prescription_new, name="prescription_new"),
    path("prescriptions/", views.prescriptions, name="prescriptions"),
    path("", views.reports, name="reports"),
]
