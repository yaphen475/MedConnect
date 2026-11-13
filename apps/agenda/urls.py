from django.urls import path

from apps.agenda import views

app_name = "agenda"

urlpatterns = [
    path("slots/", views.slot_list, name="slots"),
    path("slots/request/", views.slot_request, name="slot_request"),
    path("my/", views.my_appointments, name="my"),
    path("requests/", views.requests_list, name="requests"),
    path("requests/<int:pk>/confirm/", views.confirm_request, name="confirm"),
    path("requests/<int:pk>/refuse/", views.refuse_request, name="refuse"),
    path("new/", views.agenda_create, name="create"),
    path("<int:pk>/edit/", views.agenda_edit, name="edit"),
    path("<int:pk>/cancel/", views.agenda_cancel, name="cancel"),
    path("", views.agenda_view, name="view"),
]
