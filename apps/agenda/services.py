"""Automatic detection of available slots (US-18 — Innovation 1).

The practice is open Monday to Friday, 09:00 → 17:00, in 30 minute slots.
A slot is available when no *confirmed* appointment occupies it; pending
requests do not lock a slot (RG-05).
"""

from datetime import date as date_type, datetime, time, timedelta

from apps.agenda.models import Appointment

OPENING_TIME = time(9, 0)
CLOSING_TIME = time(17, 0)
SLOT_MINUTES = 30
OPEN_WEEKDAYS = (0, 1, 2, 3, 4)  # Monday → Friday


def practice_slots(day: date_type):
    """Every theoretical slot of ``day`` (empty when the practice is closed)."""
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
    """Start times locked by confirmed appointments (RG-04)."""
    return set(
        Appointment.objects.filter(
            date=day,
            status=Appointment.Status.CONFIRMED,
        ).values_list("start_time", flat=True)
    )


def available_slots(day: date_type):
    """Free slots of ``day``, automatically detected and sorted."""
    occupied = occupied_times(day)
    return [slot for slot in practice_slots(day) if slot not in occupied]


def is_slot_available(day: date_type, start_time: time):
    if day.weekday() not in OPEN_WEEKDAYS:
        return False
    if not (OPENING_TIME <= start_time < CLOSING_TIME):
        return False
    if start_time.minute % SLOT_MINUTES != 0:
        return False
    return start_time not in occupied_times(day)
