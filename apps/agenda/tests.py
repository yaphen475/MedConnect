from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.agenda.models import Appointment
from apps.agenda import services
from apps.patients.models import Patient

User = get_user_model()

# Monday 16 November 2026 — the practice is open.
MONDAY = date(2026, 11, 16)
SATURDAY = date(2026, 11, 21)


class AgendaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.doctor = User.objects.create_user(
            username="doc", password="Pass!2026doc", role=User.Role.DOCTOR
        )
        cls.secretary = User.objects.create_user(
            username="sec", password="Pass!2026sec", role=User.Role.SECRETARY
        )
        cls.patient_a = User.objects.create_user(
            username="pat_a", password="Pass!2026a", role=User.Role.PATIENT
        )
        cls.patient_b = User.objects.create_user(
            username="pat_b", password="Pass!2026b", role=User.Role.PATIENT
        )
        cls.admin = User.objects.create_user(
            username="adm", password="Pass!2026adm", role=User.Role.ADMIN
        )
        cls.file_a = Patient.objects.create(
            user=cls.patient_a, first_name="Alice", last_name="Armand"
        )
        cls.file_b = Patient.objects.create(
            user=cls.patient_b, first_name="Bruno", last_name="Bernard"
        )

    # --- US-05 / US-18: automatic detection of free slots ------------------

    def test_opening_hours_are_generated(self):
        slots = services.practice_slots(MONDAY)
        self.assertEqual(slots[0].hour, 9)
        self.assertEqual(slots[-1].hour, 16)
        self.assertEqual(slots[-1].minute, 30)
        self.assertEqual(services.practice_slots(SATURDAY), [])

    def test_confirmed_appointments_are_removed_from_free_slots(self):
        Appointment.objects.create(
            patient=self.file_a,
            date=MONDAY,
            start_time="09:00",
            status=Appointment.Status.CONFIRMED,
        )
        self.client.force_login(self.patient_a)
        response = self.client.get(
            reverse("agenda:slots"), {"date": MONDAY.isoformat()}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'value="09:00"')
        self.assertContains(response, 'value="09:30"')

    def test_pending_request_does_not_lock_a_slot(self):
        """RG-05: several requests can target the same slot."""
        Appointment.objects.create(
            patient=self.file_a,
            date=MONDAY,
            start_time="10:00",
            status=Appointment.Status.PENDING,
        )
        self.assertTrue(
            services.is_slot_available(MONDAY, time(9, 0))
        )
        self.assertTrue(services.is_slot_available(MONDAY, time(10, 0)))

    def test_closed_day_is_shown_as_closed(self):
        self.client.force_login(self.patient_a)
        response = self.client.get(
            reverse("agenda:slots"), {"date": SATURDAY.isoformat()}
        )
        self.assertContains(response, "Practice closed")

    # --- US-06 / RG-02 / RG-03: request of a slot -------------------------

    def test_patient_request_creates_pending_appointment(self):
        self.client.force_login(self.patient_a)
        response = self.client.post(
            reverse("agenda:slot_request"),
            {"date": MONDAY.isoformat(), "start_time": "11:00", "motif": "check"},
        )
        self.assertRedirects(response, reverse("agenda:my"))
        appointment = Appointment.objects.get()
        self.assertEqual(appointment.status, Appointment.Status.PENDING)
        self.assertEqual(appointment.patient, self.file_a)
        self.assertEqual(appointment.requested_by, self.patient_a)
        # The slot stays available (US-06: not a definitive booking).
        self.assertTrue(services.is_slot_available(MONDAY, appointment.start_time))

    def test_request_on_unavailable_slot_is_refused(self):
        Appointment.objects.create(
            patient=self.file_a,
            date=MONDAY,
            start_time="09:00",
            status=Appointment.Status.CONFIRMED,
        )
        self.client.force_login(self.patient_b)
        response = self.client.post(
            reverse("agenda:slot_request"),
            {"date": MONDAY.isoformat(), "start_time": "09:00"},
            follow=True,
        )
        self.assertContains(response, "no longer available")
        self.assertEqual(
            Appointment.objects.filter(
                start_time="09:00", status=Appointment.Status.PENDING
            ).count(),
            0,
        )

    def test_secretary_cannot_request_a_slot(self):
        self.client.force_login(self.secretary)
        response = self.client.post(
            reverse("agenda:slot_request"),
            {"date": MONDAY.isoformat(), "start_time": "11:00"},
        )
        self.assertEqual(response.status_code, 403)

    # --- US-07 / RG-01: only the secretary processes requests -------------

    def _pending(self, slot="10:30", patient=None):
        return Appointment.objects.create(
            patient=patient or self.file_a,
            date=MONDAY,
            start_time=slot,
            status=Appointment.Status.PENDING,
        )

    def test_secretary_confirms_a_request(self):
        appointment = self._pending()
        self.client.force_login(self.secretary)
        response = self.client.post(
            reverse("agenda:confirm", args=[appointment.pk])
        )
        self.assertEqual(response.status_code, 302)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.CONFIRMED)
        self.assertEqual(appointment.processed_by, self.secretary)
        # RG-04: the confirmed slot is no longer available.
        self.assertFalse(
            services.is_slot_available(appointment.date, appointment.start_time)
        )

    def test_doctor_cannot_confirm_a_request(self):
        appointment = self._pending()
        self.client.force_login(self.doctor)
        response = self.client.post(
            reverse("agenda:confirm", args=[appointment.pk])
        )
        self.assertEqual(response.status_code, 403)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.PENDING)

    def test_admin_cannot_confirm_a_request(self):
        appointment = self._pending()
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("agenda:confirm", args=[appointment.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_a_slot_can_only_host_one_confirmed_appointment(self):
        """RG-05: second confirmation of the same slot is refused."""
        first = self._pending("11:00", patient=self.file_a)
        second = self._pending("11:00", patient=self.file_b)
        self.client.force_login(self.secretary)

        self.client.post(reverse("agenda:confirm", args=[first.pk]))
        response = self.client.post(
            reverse("agenda:confirm", args=[second.pk]), follow=True
        )

        self.assertContains(response, "already confirmed")
        self.assertEqual(
            Appointment.objects.filter(
                date=MONDAY,
                start_time="11:00",
                status=Appointment.Status.CONFIRMED,
            ).count(),
            1,
        )
        second.refresh_from_db()
        self.assertEqual(second.status, Appointment.Status.PENDING)

    def test_refused_request_frees_the_slot(self):
        appointment = self._pending("13:00")
        self.client.force_login(self.secretary)
        self.client.post(reverse("agenda:refuse", args=[appointment.pk]))
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.REFUSED)
        self.assertTrue(services.is_slot_available(MONDAY, appointment.start_time))

    def test_cancelling_a_confirmed_appointment_frees_the_slot(self):
        appointment = Appointment.objects.create(
            patient=self.file_a,
            date=MONDAY,
            start_time="14:00",
            status=Appointment.Status.CONFIRMED,
        )
        self.client.force_login(self.secretary)
        self.client.post(reverse("agenda:cancel", args=[appointment.pk]))
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.CANCELLED)
        self.assertTrue(services.is_slot_available(MONDAY, appointment.start_time))

    # --- US-08: secretary manages the agenda ------------------------------

    def test_secretary_adds_an_appointment_directly(self):
        self.client.force_login(self.secretary)
        response = self.client.post(
            reverse("agenda:create"),
            {
                "patient": self.file_a.pk,
                "date": MONDAY.isoformat(),
                "start_time": "15:00",
                "motif": "direct",
            },
        )
        self.assertEqual(response.status_code, 302)
        created = Appointment.objects.get(start_time="15:00")
        self.assertEqual(created.status, Appointment.Status.CONFIRMED)
        self.assertEqual(created.processed_by, self.secretary)

    def test_direct_appointment_on_occupied_slot_is_rejected(self):
        Appointment.objects.create(
            patient=self.file_a,
            date=MONDAY,
            start_time="15:00",
            status=Appointment.Status.CONFIRMED,
        )
        self.client.force_login(self.secretary)
        response = self.client.post(
            reverse("agenda:create"),
            {
                "patient": self.file_b.pk,
                "date": MONDAY.isoformat(),
                "start_time": "15:00",
                "motif": "conflict",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already hosts a confirmed appointment")
        self.assertEqual(
            Appointment.objects.filter(start_time="15:00").count(), 1
        )

    def test_doctor_only_consults_the_agenda(self):
        self.client.force_login(self.doctor)
        response = self.client.get(reverse("agenda:view"))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse("agenda:create"),
            {
                "patient": self.file_a.pk,
                "date": MONDAY.isoformat(),
                "start_time": "15:30",
            },
        )
        self.assertEqual(response.status_code, 403)

    # --- US-09 / US-10: personal views ------------------------------------

    def test_patient_only_sees_his_own_appointments(self):
        Appointment.objects.create(
            patient=self.file_a,
            date=MONDAY,
            start_time="09:00",
            status=Appointment.Status.CONFIRMED,
            motif="Alice motif",
        )
        Appointment.objects.create(
            patient=self.file_b,
            date=MONDAY,
            start_time="09:30",
            status=Appointment.Status.CONFIRMED,
            motif="Bruno motif",
        )
        self.client.force_login(self.patient_a)
        response = self.client.get(reverse("agenda:my"))
        self.assertContains(response, "Alice motif")
        self.assertNotContains(response, "Bruno motif")

    def test_patient_cannot_open_the_cabinet_agenda(self):
        self.client.force_login(self.patient_a)
        response = self.client.get(reverse("agenda:view"))
        self.assertEqual(response.status_code, 403)

    def test_secretary_sees_pending_requests_only_in_the_queue(self):
        pending = self._pending("16:00")
        confirmed = Appointment.objects.create(
            patient=self.file_b,
            date=MONDAY,
            start_time="16:30",
            status=Appointment.Status.CONFIRMED,
        )
        self.client.force_login(self.secretary)
        response = self.client.get(reverse("agenda:requests"))
        self.assertContains(response, "16:00")
        self.assertContains(response, "16:30")  # recent decisions block
        self.assertEqual(response.status_code, 200)
