from datetime import date as date_type, datetime, time, timedelta

from django.utils import timezone

from apps.agenda.models import Appointment

OPENING_TIME = time(9, 0)
CLOSING_TIME = time(17, 0)
SLOT_MINUTES = 30
OPEN_WEEKDAYS = (0, 1, 2, 3, 4)


def practice_slots(day: date_type):
    if day.weekday() not in OPEN_WEEKDAYS:
        return []
    slots = []
    current = datetime.combine(day, OPENING_TIME)
    end = datetime.combine(day, CLOSING_TIME)
    while current < end:
        slots.append(current.time())
        current += timedelta(minutes=SLOT_MINUTES)
    return slots


def occupied_times(day: date_type):
    appointments = list(_confirmed_appointments(day))
    return {
        slot
        for slot in practice_slots(day)
        if _overlaps(appointments, day, slot, SLOT_MINUTES)
    }


def available_slots(day: date_type):
    appointments = list(_confirmed_appointments(day))
    return [
        slot
        for slot in practice_slots(day)
        if _slot_error(
            day,
            slot,
            SLOT_MINUTES,
            appointments=appointments,
        )
        is None
    ]


def is_slot_available(
    day: date_type,
    start_time: time,
    duration_minutes=SLOT_MINUTES,
    exclude_pk=None,
):
    return (
        slot_validation_error(
            day,
            start_time,
            duration_minutes,
            exclude_pk=exclude_pk,
        )
        is None
    )


def slot_validation_error(
    day,
    start_time,
    duration_minutes,
    exclude_pk=None,
    lock=False,
):
    appointments = list(
        _confirmed_appointments(
            day,
            exclude_pk=exclude_pk,
            lock=lock,
        )
    )
    return _slot_error(
        day,
        start_time,
        duration_minutes,
        appointments=appointments,
    )


def _confirmed_appointments(day, exclude_pk=None, lock=False):
    queryset = Appointment.objects.filter(
        date=day,
        status=Appointment.Status.CONFIRMED,
    )
    if exclude_pk:
        queryset = queryset.exclude(pk=exclude_pk)
    if lock:
        queryset = queryset.select_for_update()
    return queryset.only("date", "start_time", "duration_minutes")


def _slot_error(
    day,
    start_time,
    duration_minutes,
    appointments,
):
    if duration_minutes is None or duration_minutes <= 0:
        return "Appointment duration must be greater than zero."
    if day.weekday() not in OPEN_WEEKDAYS:
        return "This time is outside the practice opening hours."

    candidate_start = datetime.combine(day, start_time)
    opening = datetime.combine(day, OPENING_TIME)
    closing = datetime.combine(day, CLOSING_TIME)
    candidate_end = candidate_start + timedelta(minutes=duration_minutes)
    slot_seconds = SLOT_MINUTES * 60

    if candidate_start < opening or candidate_end > closing:
        return "This time is outside the practice opening hours."
    if (candidate_start - opening).total_seconds() % slot_seconds:
        return "This time is outside the practice opening hours."
    if _is_past(day, start_time):
        return "Appointments cannot be scheduled in the past."
    if _overlaps(appointments, day, start_time, duration_minutes):
        return (
            "This slot already hosts a confirmed appointment or overlaps "
            "an already confirmed appointment."
        )
    return None


def _overlaps(appointments, day, start_time, duration_minutes):
    candidate_start = datetime.combine(day, start_time)
    candidate_end = candidate_start + timedelta(minutes=duration_minutes)
    for appointment in appointments:
        existing_start = datetime.combine(
            appointment.date,
            appointment.start_time,
        )
        existing_end = existing_start + timedelta(
            minutes=appointment.duration_minutes
        )
        if candidate_start < existing_end and existing_start < candidate_end:
            return True
    return False


def _is_past(day, start_time):
    now = timezone.localtime()
    if day != now.date():
        return day < now.date()
    return start_time <= now.time()
