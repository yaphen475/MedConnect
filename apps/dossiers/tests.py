from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.dossiers.models import MedicalReport, Prescription, PrescriptionItem
from apps.patients.models import Patient

User = get_user_model()

DAY = date(2026, 11, 10)


class DossiersPermissionTests(TestCase):
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
        cls.report_a = MedicalReport.objects.create(
            patient=cls.file_a,
            consultation_date=DAY,
            title="Bilan annuel Alice",
            content="Contenu medical ultra prive Alice",
            author=cls.doctor,
        )
        cls.report_b = MedicalReport.objects.create(
            patient=cls.file_b,
            consultation_date=DAY,
            title="Bilan annuel Bruno",
            content="Contenu medical ultra prive Bruno",
            author=cls.doctor,
        )
        cls.prescription_a = Prescription.objects.create(
            patient=cls.file_a,
            issued_date=DAY,
            author=cls.doctor,
        )
        PrescriptionItem.objects.create(
            prescription=cls.prescription_a,
            medication="Paracetamol 500mg",
            dosage="1 comprime",
            instructions="matin et soir",
        )
        cls.prescription_b = Prescription.objects.create(
            patient=cls.file_b,
            issued_date=DAY,
            author=cls.doctor,
        )
        PrescriptionItem.objects.create(
            prescription=cls.prescription_b,
            medication="Medicament prive Bruno",
        )

    # --- US-11 / US-12 -----------------------------------------------------

    def test_doctor_reads_all_reports(self):
        self.client.force_login(self.doctor)
        response = self.client.get(reverse("dossiers:reports"))
        self.assertContains(response, "Bilan annuel Alice")
        self.assertContains(response, "Bilan annuel Bruno")

    def test_doctor_reads_patient_history_chronologically(self):
        MedicalReport.objects.create(
            patient=self.file_a,
            consultation_date=date(2025, 1, 5),
            title="Ancien bilan",
            content="plus ancien",
            author=self.doctor,
        )
        self.client.force_login(self.doctor)
        response = self.client.get(
            reverse("dossiers:patient_history", args=[self.file_a.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ancien bilan")
        self.assertContains(response, "Bilan annuel Alice")
        content = response.content.decode()
        self.assertLess(
            content.index("Ancien bilan"),
            content.index("Bilan annuel Alice"),
        )

    def test_secretary_has_no_access_to_records(self):
        """US-11 / RG-07: no medical record for the secretary."""
        self.client.force_login(self.secretary)
        for url in (
            reverse("dossiers:reports"),
            reverse("dossiers:report_new"),
            reverse("dossiers:patient_history", args=[self.file_a.pk]),
            reverse("dossiers:prescriptions"),
            reverse("dossiers:prescription_new"),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403)

    def test_admin_has_no_access_to_records(self):
        """RG-12."""
        self.client.force_login(self.admin)
        for url in (
            reverse("dossiers:reports"),
            reverse("dossiers:prescriptions"),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_patient_only_sees_his_own_reports(self):
        """US-12 / RG-06."""
        self.client.force_login(self.patient_a)
        response = self.client.get(reverse("dossiers:reports"))
        self.assertContains(response, "Bilan annuel Alice")
        self.assertNotContains(response, "Bilan annuel Bruno")

    def test_patient_cannot_open_another_patient_history(self):
        self.client.force_login(self.patient_a)
        response = self.client.get(
            reverse("dossiers:patient_history", args=[self.file_a.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_doctor_creates_a_report_for_the_right_patient(self):
        self.client.force_login(self.doctor)
        response = self.client.post(
            reverse("dossiers:report_new"),
            {
                "patient": self.file_b.pk,
                "consultation_date": "2026-11-12",
                "title": "Consultation suivie",
                "content": "Nouveau contenu",
            },
        )
        report = MedicalReport.objects.get(title="Consultation suivie")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(report.patient, self.file_b)
        self.assertEqual(report.author, self.doctor)
        self.assertEqual(report.consultation_date, date(2026, 11, 12))

    def test_patient_cannot_create_a_report(self):
        self.client.force_login(self.patient_a)
        response = self.client.get(reverse("dossiers:report_new"))
        self.assertEqual(response.status_code, 403)

    # --- US-13 / US-14 -----------------------------------------------------

    def test_patient_only_sees_his_own_prescriptions(self):
        self.client.force_login(self.patient_a)
        response = self.client.get(reverse("dossiers:prescriptions"))
        self.assertContains(response, "Paracetamol 500mg")
        self.assertNotContains(response, "Medicament prive Bruno")

    def test_patient_cannot_create_a_prescription(self):
        self.client.force_login(self.patient_a)
        response = self.client.get(reverse("dossiers:prescription_new"))
        self.assertEqual(response.status_code, 403)

    def test_doctor_creates_prescription_with_lines(self):
        self.client.force_login(self.doctor)
        response = self.client.post(
            reverse("dossiers:prescription_new"),
            {
                "patient": self.file_a.pk,
                "issued_date": "2026-11-13",
                "title": "Ordonnance test",
                "notes": "demo",
                "items-TOTAL_FORMS": "3",
                "items-INITIAL_FORMS": "0",
                "items-MIN_NUM_FORMS": "0",
                "items-MAX_NUM_FORMS": "1000",
                "items-0-medication": "Ibuprofene 400mg",
                "items-0-dosage": "1 cp",
                "items-0-instructions": "après le repas",
                "items-1-medication": "",
                "items-1-dosage": "",
                "items-1-instructions": "",
                "items-2-medication": "",
                "items-2-dosage": "",
                "items-2-instructions": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        prescription = Prescription.objects.get(title="Ordonnance test")
        self.assertEqual(prescription.patient, self.file_a)
        self.assertEqual(prescription.items.count(), 1)

    def test_empty_prescription_is_rejected(self):
        self.client.force_login(self.doctor)
        response = self.client.post(
            reverse("dossiers:prescription_new"),
            {
                "patient": self.file_a.pk,
                "issued_date": "2026-11-13",
                "title": "Vide",
                "notes": "",
                "items-TOTAL_FORMS": "3",
                "items-INITIAL_FORMS": "0",
                "items-MIN_NUM_FORMS": "0",
                "items-MAX_NUM_FORMS": "1000",
                "items-0-medication": "",
                "items-0-dosage": "",
                "items-0-instructions": "",
                "items-1-medication": "",
                "items-1-dosage": "",
                "items-1-instructions": "",
                "items-2-medication": "",
                "items-2-dosage": "",
                "items-2-instructions": "",
            },
            follow=True,
        )
        self.assertContains(response, "Add at least one medication line")
        self.assertFalse(Prescription.objects.filter(title="Vide").exists())
