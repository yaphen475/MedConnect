from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.chatbot import retrieval

User = get_user_model()


class ChatbotTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.doctor = User.objects.create_user(
            username="doc", password="Pass!2026doc", role=User.Role.DOCTOR
        )
        cls.patient = User.objects.create_user(
            username="pat", password="Pass!2026pat", role=User.Role.PATIENT
        )
        cls.admin = User.objects.create_user(
            username="adm", password="Pass!2026adm", role=User.Role.ADMIN
        )

    # --- US-19 : retrieval on the documentary base -------------------------

    def test_opening_hours_question_is_answered_with_sources(self):
        result = retrieval.answer(
            "Quels sont les horaires d'ouverture du cabinet ?"
        )
        self.assertIn("lundi au vendredi", result["text"])
        self.assertIn("Horaires du cabinet", result["sources"])

    def test_how_to_request_an_appointment_is_answered(self):
        result = retrieval.answer("Comment demander un rendez-vous ?")
        self.assertIn("secrétaire", result["text"])
        self.assertTrue(result["sources"])

    def test_unknown_question_falls_back(self):
        result = retrieval.answer("poussin violet de l'espace")
        self.assertIn("Je n'ai pas trouvé", result["text"])
        self.assertEqual(result["sources"], [])

    def test_medical_diagnosis_is_refused(self):
        """RG-13: no diagnosis, no prescription from the assistant."""
        result = retrieval.answer("Quel diagnostic pour mes maux de tete ?")
        self.assertTrue(result["refused"])
        self.assertIn("ne fournit jamais de diagnostic", result["text"])
        self.assertEqual(result["sources"], [])

    def test_retrieve_ranks_the_best_document_first(self):
        documents = retrieval.retrieve("comment contacter la secretaire")
        self.assertTrue(documents)
        self.assertEqual(documents[0]["id"], "contacter-secretaire")

    # --- Views -------------------------------------------------------------

    def test_any_role_can_use_the_assistant(self):
        for user in (self.doctor, self.patient, self.admin):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse("chatbot:chat"))
                self.assertEqual(response.status_code, 200)

    def test_login_required(self):
        response = self.client.get(reverse("chatbot:chat"))
        self.assertRedirects(
            response,
            f'{reverse("accounts:login")}?next={reverse("chatbot:chat")}',
        )

    def test_question_and_answer_are_kept_in_the_session(self):
        self.client.force_login(self.patient)
        self.client.post(
            reverse("chatbot:chat"),
            {"question": "Quels sont les horaires d'ouverture ?"},
        )
        response = self.client.post(
            reverse("chatbot:chat"),
            {"question": "Comment retrouver mes ordonnances ?"},
        )
        self.assertContains(response, "Quels sont les horaires")
        self.assertContains(response, "My prescriptions")
        self.assertEqual(len(response.context["history"]), 2)

    def test_sources_are_displayed(self):
        self.client.force_login(self.patient)
        response = self.client.post(
            reverse("chatbot:chat"),
            {"question": "Comment demander un rendez-vous ?"},
            follow=True,
        )
        self.assertContains(response, "Sources")

    def test_clear_empties_the_history(self):
        self.client.force_login(self.patient)
        self.client.post(
            reverse("chatbot:chat"),
            {"question": "Comment contacter la secretaire ?"},
        )
        response = self.client.post(reverse("chatbot:clear"))
        self.assertEqual(response.context["history"], [])
