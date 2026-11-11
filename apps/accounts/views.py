from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.accounts.models import User


ROLE_NAVIGATION = {
    User.Role.ADMIN: (
        {"label": "Users", "icon": "bi-people", "slug": "users"},
        {"label": "Settings", "icon": "bi-gear", "slug": "settings"},
    ),
    User.Role.DOCTOR: (
        {
            "label": "Appointments",
            "icon": "bi-calendar-check",
            "slug": "appointments",
        },
        {"label": "Patients", "icon": "bi-person-vcard", "slug": "patients"},
        {
            "label": "Medical Records",
            "icon": "bi-file-medical",
            "slug": "medical-records",
        },
    ),
    User.Role.SECRETARY: (
        {
            "label": "Appointment Requests",
            "icon": "bi-calendar-plus",
            "slug": "appointment-requests",
        },
        {"label": "Schedule", "icon": "bi-calendar-week", "slug": "schedule"},
        {"label": "Patients", "icon": "bi-person-vcard", "slug": "patients"},
    ),
    User.Role.PATIENT: (
        {
            "label": "My Appointments",
            "icon": "bi-calendar-check",
            "slug": "my-appointments",
        },
        {
            "label": "Request Appointment",
            "icon": "bi-calendar-plus",
            "slug": "request-appointment",
        },
        {
            "label": "Prescriptions",
            "icon": "bi-capsule",
            "slug": "prescriptions",
        },
    ),
}

ROLE_LABELS = {
    User.Role.ADMIN: "Technical administrator",
    User.Role.DOCTOR: "Doctor",
    User.Role.SECRETARY: "Medical secretary",
    User.Role.PATIENT: "Patient",
}


def home(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    return redirect("accounts:login")


@login_required
def dashboard(request):
    context = {
        "navigation_items": ROLE_NAVIGATION.get(request.user.role, ()),
        "role_label": ROLE_LABELS.get(request.user.role, request.user.role),
    }
    return render(request, "accounts/dashboard.html", context)
