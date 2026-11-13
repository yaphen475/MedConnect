from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.patients.models import Patient

User = get_user_model()

SECRET_MEDICAL = "Antecedents cardiologiques secrets"


class PatientPermissionTests(TestCase):
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
            user=cls.patient_a,
            first_name="Alice",
            last_name="Armand",
            phone="0600000001",
            medical_notes=SECRET_MEDICAL,
            administrative_notes="Dossier administratif A",
        )
        cls.file_b = Patient.objects.create(
            user=cls.patient_b,
            first_name="Bruno",
            last_name="Bernard",
            medical_notes="B antecedent",
        )

    def test_login_required_on_list(self):
        response = self.client.get(reverse("patients:list"))
        self.assertRedirects(
            response,
            f'{reverse("accounts:login")}?next={reverse("patients:list")}',
        )

    def test_doctor_sees_medical_data(self):
        self.client.force_login(self.doctor)
        response = self.client.get(reverse("patients:list"))
        self.assertContains(response, "Alice")
        response = self.client.get(
            reverse("patients:detail", args=[self.file_a.pk])
        )
        self.assertContains(response, SECRET_MEDICAL)

    def test_secretary_list_and_detail_hide_medical_data(self):
        """US-04 / RG-07: the secretary never sees medical fields."""
        self.client.force_login(self.secretary)
        response = self.client.get(reverse("patients:list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, SECRET_MEDICAL)

        response = self.client.get(
            reverse("patients:detail", args=[self.file_a.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Restricted area")
        self.assertNotContains(response, SECRET_MEDICAL)

    def test_admin_has_no_access_to_patient_data(self):
        """RG-12: the technical administrator has no medical/data access."""
        self.client.force_login(self.admin)
        for url in (
            reverse("patients:list"),
            reverse("patients:detail", args=[self.file_a.pk]),
            reverse("patients:create"),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403)

    def test_patient_only_reads_his_own_file(self):
        """RG-06."""
        self.client.force_login(self.patient_a)
        response = self.client.get(reverse("patients:list"), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alice")

        response = self.client.get(
            reverse("patients:detail", args=[self.file_a.pk])
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("patients:detail", args=[self.file_b.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_secretary_cannot_write_medical_notes(self):
        """US-04: medical fields cannot be forged by a non-doctor."""
        self.client.force_login(self.secretary)
        url = reverse("patients:edit", args=[self.file_a.pk])
        response = self.client.post(
            url,
            {
                "first_name": "Alice",
                "last_name": "Armand",
                "birth_date": "",
                "phone": "0611111111",
                "email": "",
                "address": "1 rue de la Paix",
                "social_security_number": "",
                "administrative_notes": "updated by secretary",
                "medical_notes": "HACKED BY SECRETARY",
                "user": self.patient_a.pk,
            },
        )
        self.file_a.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.file_a.medical_notes, SECRET_MEDICAL)
        self.assertEqual(self.file_a.phone, "0611111111")

    def test_doctor_can_update_medical_notes(self):
        self.client.force_login(self.doctor)
        url = reverse("patients:edit", args=[self.file_a.pk])
        self.client.post(
            url,
            {
                "first_name": "Alice",
                "last_name": "Armand",
                "birth_date": "1980-04-12",
                "phone": "0622222222",
                "email": "alice@example.com",
                "address": "2 rue des Lilas",
                "social_security_number": "1 80 04 75 111 111 42",
                "administrative_notes": "updated by doctor",
                "medical_notes": "Nouvelles observations",
                "user": self.patient_a.pk,
            },
        )
        self.file_a.refresh_from_db()
        self.assertEqual(self.file_a.medical_notes, "Nouvelles observations")
        self.assertEqual(self.file_a.birth_date.isoformat(), "1980-04-12")

    def test_secretary_can_create_a_patient_file(self):
        self.client.force_login(self.secretary)
        response = self.client.post(
            reverse("patients:create"),
            {
                "first_name": "Charlie",
                "last_name": "Chevalier",
                "birth_date": "1991-01-01",
                "phone": "0633333333",
                "email": "charlie@example.com",
                "address": "",
                "social_security_number": "",
                "administrative_notes": "",
                "medical_notes": "should be ignored",
            },
        )
        self.assertEqual(response.status_code, 302)
        created = Patient.objects.get(last_name="Chevalier")
        self.assertEqual(created.medical_notes, "")

    def test_patient_cannot_create_a_file(self):
        self.client.force_login(self.patient_a)
        response = self.client.get(reverse("patients:create"))
        self.assertEqual(response.status_code, 403)

    def test_secretary_never_sees_nor_writes_the_ssn(self):
        """RG-08: data not needed at the reception desk are masked."""
        SSN = "1 80 04 75 111 111 42"
        self.file_a.social_security_number = SSN
        self.file_a.save(update_fields=["social_security_number"])

        self.client.force_login(self.secretary)

        # Masked on the detail page.
        response = self.client.get(
            reverse("patients:detail", args=[self.file_a.pk])
        )
        self.assertNotContains(response, SSN)
        self.assertContains(response, "Restricted — RG-08")

        # Absent from the edit form.
        response = self.client.get(
            reverse("patients:edit", args=[self.file_a.pk])
        )
        self.assertNotContains(response, SSN)
        self.assertNotContains(response, "social_security_number")

        # A posted value is ignored (field removed for the secretary).
        self.client.post(
            reverse("patients:edit", args=[self.file_a.pk]),
            {
                "first_name": "Alice",
                "last_name": "Armand",
                "birth_date": "",
                "phone": "0600000001",
                "email": "",
                "address": "",
                "social_security_number": "FORGED-BY-SECRETARY",
                "administrative_notes": "",
                "user": self.patient_a.pk,
            },
        )
        self.file_a.refresh_from_db()
        self.assertEqual(self.file_a.social_security_number, SSN)

    def test_doctor_sees_the_ssn(self):
        SSN = "1 80 04 75 111 111 42"
        self.file_a.social_security_number = SSN
        self.file_a.save(update_fields=["social_security_number"])

        self.client.force_login(self.doctor)
        response = self.client.get(
            reverse("patients:detail", args=[self.file_a.pk])
        )
        self.assertContains(response, SSN)

    def test_patient_reads_his_own_ssn(self):
        SSN = "1 80 04 75 111 111 42"
        self.file_a.social_security_number = SSN
        self.file_a.save(update_fields=["social_security_number"])

        self.client.force_login(self.patient_a)
        response = self.client.get(
            reverse("patients:detail", args=[self.file_a.pk])
        )
        self.assertContains(response, SSN)
