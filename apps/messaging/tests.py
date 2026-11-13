from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.messaging.models import Conversation, Message

User = get_user_model()


class MessagingTests(TestCase):
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

        cls.thread_doctor_a, _ = Conversation.direct(cls.doctor, cls.patient_a)
        Message.objects.create(
            conversation=cls.thread_doctor_a,
            sender=cls.doctor,
            body="Bonjour Alice, message prive medecin",
        )
        cls.thread_doctor_b, _ = Conversation.direct(cls.doctor, cls.patient_b)
        Message.objects.create(
            conversation=cls.thread_doctor_b,
            sender=cls.doctor,
            body="Bonjour Bruno, message prive medecin B",
        )

    def test_login_required(self):
        response = self.client.get(reverse("messaging:inbox"))
        self.assertRedirects(
            response,
            f'{reverse("accounts:login")}?next={reverse("messaging:inbox")}',
        )

    def test_inbox_shows_only_my_conversations(self):
        """US-16 / RG-11."""
        self.client.force_login(self.patient_a)
        response = self.client.get(reverse("messaging:inbox"))
        self.assertContains(response, "doc")
        self.assertNotContains(response, "pat_b")
        self.assertNotContains(response, "message prive medecin B")

    def test_participant_can_read_and_post(self):
        """US-15 / US-16."""
        self.client.force_login(self.patient_a)
        response = self.client.get(
            reverse("messaging:thread", args=[self.thread_doctor_a.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "message prive medecin")

        self.client.post(
            reverse("messaging:thread", args=[self.thread_doctor_a.pk]),
            {"body": "Reponse de Alice"},
        )
        self.assertTrue(
            Message.objects.filter(
                conversation=self.thread_doctor_a,
                sender=self.patient_a,
                body="Reponse de Alice",
            ).exists()
        )

    def test_non_participant_is_forbidden(self):
        """US-17 / RG-11: patient B cannot open the thread of patient A."""
        self.client.force_login(self.patient_b)
        response = self.client.get(
            reverse("messaging:thread", args=[self.thread_doctor_a.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_has_no_access_to_messaging(self):
        """RG-12 / matrix: « Messagerie — Admin : sans accès au contenu »."""
        self.client.force_login(self.admin)
        for url in (
            reverse("messaging:inbox"),
            reverse("messaging:compose"),
            reverse("messaging:thread", args=[self.thread_doctor_a.pk]),
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_secretary_and_doctor_can_talk(self):
        conversation, created = Conversation.direct(
            self.secretary, self.doctor
        )
        self.assertTrue(created)
        self.client.force_login(self.secretary)
        self.client.post(
            reverse("messaging:thread", args=[conversation.pk]),
            {"body": "Planning du jour"},
        )
        self.assertEqual(
            conversation.messages.filter(sender=self.secretary).count(), 1
        )

    def test_conversation_is_reused_between_the_same_pair(self):
        second, created = Conversation.direct(self.doctor, self.patient_a)
        self.assertFalse(created)
        self.assertEqual(second.pk, self.thread_doctor_a.pk)

    def test_patient_cannot_write_to_another_patient(self):
        """Authorised recipients only (US-15)."""
        self.client.force_login(self.patient_a)
        response = self.client.post(
            reverse("messaging:compose"),
            {
                "recipient": self.patient_b.pk,
                "body": "cross patient message",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select a valid choice")
        self.assertFalse(
            Message.objects.filter(body="cross patient message").exists()
        )

    def test_patient_cannot_start_a_conversation_with_another_patient(self):
        self.client.force_login(self.patient_a)

        response = self.client.post(
            reverse("messaging:start", args=[self.patient_b.pk])
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Conversation.objects.filter(participants=self.patient_a)
            .filter(participants=self.patient_b)
            .exists()
        )

    def test_user_cannot_start_a_conversation_with_self(self):
        self.client.force_login(self.doctor)
        initial_count = Conversation.objects.filter(
            participants=self.doctor
        ).count()

        response = self.client.post(
            reverse("messaging:start", args=[self.doctor.pk])
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Conversation.objects.filter(participants=self.doctor).count(),
            initial_count,
        )

    def test_cannot_send_a_message_to_the_administrator(self):
        self.client.force_login(self.doctor)
        response = self.client.post(
            reverse("messaging:compose"),
            {"recipient": self.admin.pk, "body": "should not pass"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Message.objects.filter(body="should not pass").exists()
        )

    def test_history_is_chronological(self):
        """US-16."""
        Message.objects.create(
            conversation=self.thread_doctor_a,
            sender=self.patient_a,
            body="Deuxieme message",
        )
        self.client.force_login(self.patient_a)
        response = self.client.get(
            reverse("messaging:thread", args=[self.thread_doctor_a.pk])
        )
        content = response.content.decode()
        self.assertLess(
            content.index("message prive medecin"),
            content.index("Deuxieme message"),
        )
