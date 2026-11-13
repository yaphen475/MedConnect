from django.urls import reverse

from apps.accounts.models import User


ROLE_LABELS = {
    User.Role.ADMIN: "Technical administrator",
    User.Role.DOCTOR: "Doctor",
    User.Role.SECRETARY: "Medical secretary",
    User.Role.PATIENT: "Patient",
}

NAVIGATION_BY_ROLE = {
    User.Role.ADMIN: (
        {
            "label": "Assistant",
            "icon": "bi-robot",
            "section": "chatbot",
            "namespace": "chatbot",
            "url_name": "chatbot:chat",
            "description": "Open the administrative assistant.",
        },
        {
            "label": "Users",
            "icon": "bi-people",
            "section": "users",
            "description": "User administration will be available here.",
        },
        {
            "label": "Settings",
            "icon": "bi-gear",
            "section": "settings",
            "description": "Application settings will be available here.",
        },
    ),
    User.Role.DOCTOR: (
        {
            "label": "Patients",
            "icon": "bi-person-vcard",
            "section": "patients",
            "namespace": "patients",
            "url_name": "patients:list",
            "description": "Open patient files and clinical information.",
        },
        {
            "label": "Cabinet Schedule",
            "icon": "bi-calendar-week",
            "section": "agenda",
            "namespace": "agenda",
            "url_name": "agenda:view",
            "description": "Review the cabinet appointment schedule.",
        },
        {
            "label": "Medical Records",
            "icon": "bi-file-medical",
            "section": "records",
            "namespace": "dossiers",
            "url_name": "dossiers:reports",
            "description": "Review and maintain medical reports.",
        },
        {
            "label": "Prescriptions",
            "icon": "bi-capsule",
            "section": "prescriptions",
            "namespace": "dossiers",
            "url_name": "dossiers:prescriptions",
            "description": "Review and prepare prescriptions.",
        },
        {
            "label": "Messaging",
            "icon": "bi-chat-dots",
            "section": "messaging",
            "namespace": "messaging",
            "url_name": "messaging:inbox",
            "description": "Open secure conversations.",
        },
        {
            "label": "Assistant",
            "icon": "bi-robot",
            "section": "chatbot",
            "namespace": "chatbot",
            "url_name": "chatbot:chat",
            "description": "Ask the administrative assistant for guidance.",
        },
    ),
    User.Role.SECRETARY: (
        {
            "label": "Patients",
            "icon": "bi-person-vcard",
            "section": "patients",
            "namespace": "patients",
            "url_name": "patients:list",
            "description": "Open patient administrative files.",
        },
        {
            "label": "Cabinet Schedule",
            "icon": "bi-calendar-week",
            "section": "agenda",
            "namespace": "agenda",
            "url_name": "agenda:view",
            "description": "Manage the cabinet appointment schedule.",
        },
        {
            "label": "Appointment Requests",
            "icon": "bi-calendar-plus",
            "section": "requests",
            "namespace": "agenda",
            "url_name": "agenda:requests",
            "description": "Review pending appointment requests.",
        },
        {
            "label": "Messaging",
            "icon": "bi-chat-dots",
            "section": "messaging",
            "namespace": "messaging",
            "url_name": "messaging:inbox",
            "description": "Open secure conversations.",
        },
        {
            "label": "Assistant",
            "icon": "bi-robot",
            "section": "chatbot",
            "namespace": "chatbot",
            "url_name": "chatbot:chat",
            "description": "Ask the administrative assistant for guidance.",
        },
    ),
    User.Role.PATIENT: (
        {
            "label": "My File",
            "icon": "bi-person-vcard",
            "section": "patients",
            "namespace": "patients",
            "url_name": "patients:mine",
            "description": "Open your personal patient file.",
        },
        {
            "label": "Request Appointment",
            "icon": "bi-calendar-plus",
            "section": "slots",
            "namespace": "agenda",
            "url_name": "agenda:slots",
            "description": "Choose an available appointment slot.",
        },
        {
            "label": "My Appointments",
            "icon": "bi-calendar-check",
            "section": "my-appointments",
            "namespace": "agenda",
            "url_name": "agenda:my",
            "description": "Review your appointment history and requests.",
        },
        {
            "label": "My Medical Reports",
            "icon": "bi-file-medical",
            "section": "records",
            "namespace": "dossiers",
            "url_name": "dossiers:reports",
            "description": "Review your available medical reports.",
        },
        {
            "label": "My Prescriptions",
            "icon": "bi-capsule",
            "section": "prescriptions",
            "namespace": "dossiers",
            "url_name": "dossiers:prescriptions",
            "description": "Review your available prescriptions.",
        },
        {
            "label": "Messaging",
            "icon": "bi-chat-dots",
            "section": "messaging",
            "namespace": "messaging",
            "url_name": "messaging:inbox",
            "description": "Open secure conversations.",
        },
        {
            "label": "Assistant",
            "icon": "bi-robot",
            "section": "chatbot",
            "namespace": "chatbot",
            "url_name": "chatbot:chat",
            "description": "Ask the administrative assistant for guidance.",
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
