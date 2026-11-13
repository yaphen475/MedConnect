from datetime import date as date_type, timedelta

from django.contrib import messages
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.agenda import services
from apps.agenda.forms import DirectAppointmentForm, EditAppointmentForm
from apps.agenda.models import Appointment
from apps.core.permissions import role_required
from apps.patients.models import Patient

DOCTOR = "DOCTOR"
SECRETARY = "SECRETARY"
PATIENT = "PATIENT"


def _selected_date(request):
    raw = request.GET.get("date") or request.POST.get("date")
    try:
        return date_type.fromisoformat(raw)
    except (TypeError, ValueError):
        return timezone.localdate()


def _shift(day, offset):
    return day + timedelta(days=offset)


# --- Patient side (US-05, US-06, US-09, US-10, US-18) ---------------------


@role_required(PATIENT)
def slot_list(request):
    """US-05 / US-18: automatically detected available slots."""
    day = _selected_date(request)
    slots = services.available_slots(day)
    context = {
        "day": day,
        "slots": slots,
        "previous_day": _shift(day, -1),
        "next_day": _shift(day, 1),
        "closed": day.weekday() not in services.OPEN_WEEKDAYS,
        "section": "slots",
    }
    return render(request, "agenda/slots.html", context)


@role_required(PATIENT)
@require_POST
def slot_request(request):
    """US-06 / RG-02 / RG-03: a patient only asks for a free slot."""
    day = _selected_date(request)
    raw_time = request.POST.get("start_time", "")
    try:
        start_time = timezone.datetime.strptime(raw_time, "%H:%M").time()
    except ValueError:
        messages.error(request, "Please choose one of the proposed slots.")
        return redirect("agenda:slots")

    if not services.is_slot_available(day, start_time):
        messages.error(
            request, "This slot is no longer available, please pick another one."
        )
        return redirect("agenda:slots")

    profile, _created = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            "first_name": request.user.first_name or "",
            "last_name": request.user.last_name or "",
        },
    )
    appointment = Appointment.objects.create(
        patient=profile,
        date=day,
        start_time=start_time,
        motif=request.POST.get("motif", "").strip(),
        status=Appointment.Status.PENDING,
        requested_by=request.user,
    )
    messages.success(
        request,
        f"Request sent for {appointment.date:%d/%m/%Y} at "
        f"{appointment.start_time:%H:%M} — waiting for the secretary.",
    )
    return redirect("agenda:my")


@role_required(PATIENT)
def my_appointments(request):
    """US-09 / US-10: the patient only sees his own appointments."""
    appointments = Appointment.objects.filter(
        patient__user=request.user
    ).select_related("patient")
    context = {
        "appointments": appointments,
        "section": "my-appointments",
    }
    return render(request, "agenda/my.html", context)


# --- Secretary side (US-07, US-08) ----------------------------------------


@role_required(SECRETARY)
def requests_list(request):
    """US-07: pending requests, accept or refuse (RG-1: secretary only)."""
    pending = (
        Appointment.objects.filter(status=Appointment.Status.PENDING)
        .select_related("patient")
    )
    processed = (
        Appointment.objects.exclude(status=Appointment.Status.PENDING)
        .select_related("patient", "processed_by")[:10]
    )
    context = {
        "pending": pending,
        "processed": processed,
        "section": "requests",
    }
    return render(request, "agenda/requests.html", context)


@role_required(SECRETARY)
@require_POST
def confirm_request(request, pk):
    """US-07 / RG-01 / RG-04 / RG-05: only one confirmed appointment per slot."""
    appointment = get_object_or_404(Appointment, pk=pk)
    if appointment.status != Appointment.Status.PENDING:
        messages.error(request, "This request has already been processed.")
        return redirect("agenda:requests")

    try:
        with transaction.atomic():
            if not services.is_slot_available(
                appointment.date, appointment.start_time
            ):
                raise IntegrityError("slot already confirmed")
            appointment.status = Appointment.Status.CONFIRMED
            appointment.processed_by = request.user
            appointment.save(
                update_fields=["status", "processed_by", "updated_at"]
            )
    except IntegrityError:
        messages.error(
            request,
            "Impossible: another appointment already confirmed on this slot.",
        )
    else:
        messages.success(
            request,
            f"Appointment confirmed for {appointment.patient} "
            f"on {appointment.date:%d/%m/%Y} at {appointment.start_time:%H:%M}.",
        )
    return redirect("agenda:requests")


@role_required(SECRETARY)
@require_POST
def refuse_request(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if appointment.status != Appointment.Status.PENDING:
        messages.error(request, "This request has already been processed.")
        return redirect("agenda:requests")
    appointment.status = Appointment.Status.REFUSED
    appointment.processed_by = request.user
    appointment.save(update_fields=["status", "processed_by", "updated_at"])
    messages.info(request, "Request refused. The slot stays available.")
    return redirect("agenda:requests")


@role_required(SECRETARY)
def agenda_create(request):
    """US-08: the secretary can add an appointment directly (confirmed)."""
    if request.method == "POST":
        form = DirectAppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = Appointment.Status.CONFIRMED
            appointment.processed_by = request.user
            appointment.save()
            messages.success(request, "Appointment added to the agenda.")
            return redirect("agenda:view")
    else:
        form = DirectAppointmentForm(initial={"date": _selected_date(request)})
    return render(
        request,
        "agenda/appointment_form.html",
        {"form": form, "title": "New appointment", "section": "agenda"},
    )


@role_required(SECRETARY)
def agenda_edit(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == "POST":
        form = EditAppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated.")
            return redirect("agenda:view")
    else:
        form = EditAppointmentForm(instance=appointment)
    return render(
        request,
        "agenda/appointment_form.html",
        {
            "form": form,
            "title": f"Edit appointment #{appointment.pk}",
            "appointment": appointment,
            "section": "agenda",
        },
    )


@role_required(SECRETARY)
@require_POST
def agenda_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if appointment.status != Appointment.Status.CONFIRMED:
        messages.error(request, "Only a confirmed appointment can be cancelled.")
        return redirect("agenda:view")
    appointment.status = Appointment.Status.CANCELLED
    appointment.processed_by = request.user
    appointment.save(update_fields=["status", "processed_by", "updated_at"])
    messages.info(
        request, "Appointment cancelled, the slot is available again."
    )
    return redirect("agenda:view")


# --- Doctor side (US-09) ---------------------------------------------------


@role_required(DOCTOR, SECRETARY)
def agenda_view(request):
    """US-08 / US-09: consultation of the cabinet agenda."""
    day = _selected_date(request)
    appointments = (
        Appointment.objects.filter(date=day)
        .exclude(status=Appointment.Status.REFUSED)
        .select_related("patient", "requested_by")
    )
    context = {
        "appointments": appointments,
        "day": day,
        "previous_day": _shift(day, -1),
        "next_day": _shift(day, 1),
        "available_count": len(services.available_slots(day)),
        "is_secretary": request.user.role == SECRETARY,
        "section": "agenda",
    }
    return render(request, "agenda/agenda.html", context)
