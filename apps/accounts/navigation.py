from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User


ROLE_LABELS = {
    User.Role.ADMIN: _("Technical administrator"),
    User.Role.DOCTOR: _("Doctor"),
    User.Role.SECRETARY: _("Medical secretary"),
    User.Role.PATIENT: _("Patient"),
}

NAVIGATION_BY_ROLE = {
    User.Role.ADMIN: (
        {
            "label": _("Assistant"),
            "icon": "bi-robot",
            "section": "chatbot",
            "namespace": "chatbot",
            "url_name": "chatbot:chat",
            "description": _("Open the administrative assistant."),
        },
        {
            "label": _("Users"),
            "icon": "bi-people",
            "section": "users",
            "description": _("User administration will be available here."),
        },
        {
            "label": _("Settings"),
            "icon": "bi-gear",
            "section": "settings",
            "description": _("Application settings will be available here."),
        },
    ),
    User.Role.DOCTOR: (
        {
            "label": _("Patients"),
            "icon": "bi-person-vcard",
            "section": "patients",
            "namespace": "patients",
            "url_name": "patients:list",
            "description": _("Open patient files and clinical information."),
        },
        {
            "label": _("Cabinet Schedule"),
            "icon": "bi-calendar-week",
            "section": "agenda",
            "namespace": "agenda",
            "url_name": "agenda:view",
            "description": _("Review the cabinet appointment schedule."),
        },
        {
            "label": _("Medical Records"),
            "icon": "bi-file-medical",
            "section": "records",
            "namespace": "dossiers",
            "url_name": "dossiers:reports",
            "description": _("Review and maintain medical reports."),
        },
        {
            "label": _("Prescriptions"),
            "icon": "bi-capsule",
            "section": "prescriptions",
            "namespace": "dossiers",
            "url_name": "dossiers:prescriptions",
            "description": _("Review and prepare prescriptions."),
        },
        {
            "label": _("Messaging"),
            "icon": "bi-chat-dots",
            "section": "messaging",
            "namespace": "messaging",
            "url_name": "messaging:inbox",
            "description": _("Open secure conversations."),
        },
        {
            "label": _("Assistant"),
            "icon": "bi-robot",
            "section": "chatbot",
            "namespace": "chatbot",
            "url_name": "chatbot:chat",
            "description": _("Ask the administrative assistant for guidance."),
        },
    ),
    User.Role.SECRETARY: (
        {
            "label": _("Patients"),
            "icon": "bi-person-vcard",
            "section": "patients",
            "namespace": "patients",
            "url_name": "patients:list",
            "description": _("Open patient administrative files."),
        },
        {
            "label": _("Cabinet Schedule"),
            "icon": "bi-calendar-week",
            "section": "agenda",
            "namespace": "agenda",
            "url_name": "agenda:view",
            "description": _("Manage the cabinet appointment schedule."),
        },
        {
            "label": _("Appointment Requests"),
            "icon": "bi-calendar-plus",
            "section": "requests",
            "namespace": "agenda",
            "url_name": "agenda:requests",
            "description": _("Review pending appointment requests."),
        },
        {
            "label": _("Messaging"),
            "icon": "bi-chat-dots",
            "section": "messaging",
            "namespace": "messaging",
            "url_name": "messaging:inbox",
            "description": _("Open secure conversations."),
        },
        {
            "label": _("Assistant"),
            "icon": "bi-robot",
            "section": "chatbot",
            "namespace": "chatbot",
            "url_name": "chatbot:chat",
            "description": _("Ask the administrative assistant for guidance."),
        },
    ),
    User.Role.PATIENT: (
        {
            "label": _("My File"),
            "icon": "bi-person-vcard",
            "section": "patients",
            "namespace": "patients",
            "url_name": "patients:mine",
            "description": _("Open your personal patient file."),
        },
        {
            "label": _("Request Appointment"),
            "icon": "bi-calendar-plus",
            "section": "slots",
            "namespace": "agenda",
            "url_name": "agenda:slots",
            "description": _("Choose an available appointment slot."),
        },
        {
            "label": _("My Appointments"),
            "icon": "bi-calendar-check",
            "section": "my-appointments",
            "namespace": "agenda",
            "url_name": "agenda:my",
            "description": _("Review your appointment history and requests."),
        },
        {
            "label": _("My Medical Reports"),
            "icon": "bi-file-medical",
            "section": "records",
            "namespace": "dossiers",
            "url_name": "dossiers:reports",
            "description": _("Review your available medical reports."),
        },
        {
            "label": _("My Prescriptions"),
            "icon": "bi-capsule",
            "section": "prescriptions",
            "namespace": "dossiers",
            "url_name": "dossiers:prescriptions",
            "description": _("Review your available prescriptions."),
        },
        {
            "label": _("Messaging"),
            "icon": "bi-chat-dots",
            "section": "messaging",
            "namespace": "messaging",
            "url_name": "messaging:inbox",
            "description": _("Open secure conversations."),
        },
        {
            "label": _("Assistant"),
            "icon": "bi-robot",
            "section": "chatbot",
            "namespace": "chatbot",
            "url_name": "chatbot:chat",
            "description": _("Ask the administrative assistant for guidance."),
        },
    ),
}


def navigation_for(user):
    items = NAVIGATION_BY_ROLE.get(user.role, ())
    return tuple(
        {
            **item,
            "url": reverse(item["url_name"]) if item.get("url_name") else None,
        }
        for item in items
    )
