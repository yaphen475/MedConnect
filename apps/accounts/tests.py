import os
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse


class AuthenticationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "TestPassword!2026"
        cls.user = get_user_model().objects.create_user(
            username="doctor_test",
            password=cls.password,
            role=get_user_model().Role.DOCTOR,
        )

    def test_successful_login(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": self.user.username, "password": self.password},
        )

        self.assertRedirects(response, reverse("accounts:dashboard"))
        self.assertEqual(
            self.client.session.get("_auth_user_id"),
            str(self.user.pk),
        )

    def test_invalid_credentials(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": self.user.username, "password": "invalid-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Invalid username or password.",
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("accounts:dashboard"))

        self.assertRedirects(
            response,
            f'{reverse("accounts:login")}?next={reverse("accounts:dashboard")}',
        )

    def test_authenticated_user_can_access_dashboard(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, "Doctor")

    def test_all_roles_are_persisted(self):
        user_model = get_user_model()

        for index, role in enumerate(user_model.Role.values):
            with self.subTest(role=role):
                user = user_model.objects.create_user(
                    username=f"role_test_{index}",
                    password=self.password,
                    role=role,
                )
                user.refresh_from_db()
                self.assertEqual(user.role, role)

    def test_logout_invalidates_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_form_does_not_expose_role(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertNotIn("role", response.context["form"].fields)

    def test_home_redirects_unauthenticated_user_to_login(self):
        response = self.client.get(reverse("accounts:home"))

        self.assertRedirects(response, reverse("accounts:login"))

    def test_home_redirects_authenticated_user_to_dashboard(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:home"))

        self.assertRedirects(response, reverse("accounts:dashboard"))

    def test_dashboard_navigation_matches_user_role(self):
        user_model = get_user_model()
        expected_navigation = {
            user_model.Role.ADMIN: (
                ("Assistant", "chatbot:chat"),
                ("Users", None),
                ("Settings", None),
            ),
            user_model.Role.DOCTOR: (
                ("Patients", "patients:list"),
                ("Cabinet Schedule", "agenda:view"),
                ("Medical Records", "dossiers:reports"),
                ("Prescriptions", "dossiers:prescriptions"),
                ("Messaging", "messaging:inbox"),
                ("Assistant", "chatbot:chat"),
            ),
            user_model.Role.SECRETARY: (
                ("Patients", "patients:list"),
                ("Cabinet Schedule", "agenda:view"),
                ("Appointment Requests", "agenda:requests"),
                ("Messaging", "messaging:inbox"),
                ("Assistant", "chatbot:chat"),
            ),
            user_model.Role.PATIENT: (
                ("My File", "patients:mine"),
                ("Request Appointment", "agenda:slots"),
                ("My Appointments", "agenda:my"),
                ("My Medical Reports", "dossiers:reports"),
                ("My Prescriptions", "dossiers:prescriptions"),
                ("Messaging", "messaging:inbox"),
                ("Assistant", "chatbot:chat"),
            ),
        }

        for index, (role, items) in enumerate(expected_navigation.items()):
            with self.subTest(role=role):
                user = user_model.objects.create_user(
                    username=f"navigation_test_{index}",
                    password=self.password,
                    role=role,
                )
                self.client.force_login(user)
                response = self.client.get(reverse("accounts:dashboard"))

                rendered_items = response.context["navigation_items"]
                self.assertEqual(
                    tuple(item["label"] for item in rendered_items),
                    tuple(label for label, url_name in items),
                )
                for label, url_name in items:
                    self.assertContains(response, label)
                    if url_name:
                        url = reverse(url_name)
                        self.assertContains(
                            response,
                            f'class="module-card module-card-link h-100" href="{url}"',
                            html=False,
                        )
                        target = self.client.get(url)
                        self.assertNotIn(target.status_code, (403, 404))
                expected_soon = sum(url_name is None for label, url_name in items)
                self.assertContains(
                    response,
                    "Coming soon",
                    count=expected_soon,
                )

    def test_unauthorized_module_access_returns_forbidden(self):
        user_model = get_user_model()
        cases = (
            (user_model.Role.ADMIN, "patients:list"),
            (user_model.Role.DOCTOR, "agenda:requests"),
            (user_model.Role.SECRETARY, "dossiers:reports"),
            (user_model.Role.PATIENT, "agenda:view"),
        )

        for index, (role, url_name) in enumerate(cases):
            with self.subTest(role=role, url_name=url_name):
                user = user_model.objects.create_user(
                    username=f"forbidden_test_{index}",
                    password=self.password,
                    role=role,
                )
                self.client.force_login(user)
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 403)

    def test_dashboard_and_modules_use_shared_layout(self):
        self.client.force_login(self.user)

        dashboard_response = self.client.get(reverse("accounts:dashboard"))
        module_response = self.client.get(reverse("patients:list"))

        self.assertTemplateUsed(
            dashboard_response,
            "accounts/app_layout.html",
        )
        self.assertTemplateUsed(module_response, "modules/layout.html")
        self.assertTemplateUsed(
            module_response,
            "accounts/app_layout.html",
        )
        self.assertContains(module_response, 'id="appSidebar"', count=1)
        self.assertContains(
            module_response,
            f'class="sidebar-link active" href="{reverse("patients:list")}"',
            html=False,
        )


class DemoUsersCommandTests(TestCase):
    @override_settings(DEBUG=True)
    def test_command_is_idempotent(self):
        password = "DemoCommandTest!2026"

        with patch.dict(os.environ, {"MEDCONNECT_DEMO_PASSWORD": password}):
            call_command("seed_demo_users", stdout=StringIO())
            call_command("seed_demo_users", stdout=StringIO())

        user_model = get_user_model()
        expected_roles = {
            "admin_demo": user_model.Role.ADMIN,
            "doctor_demo": user_model.Role.DOCTOR,
            "secretary_demo": user_model.Role.SECRETARY,
            "patient_demo": user_model.Role.PATIENT,
        }
        self.assertEqual(
            user_model.objects.filter(username__in=expected_roles).count(),
            4,
        )

        for username, role in expected_roles.items():
            with self.subTest(username=username):
                user = user_model.objects.get(username=username)
                self.assertEqual(user.role, role)
                self.assertTrue(user.check_password(password))
                self.assertFalse(user.is_staff)
                self.assertFalse(user.is_superuser)

    @override_settings(DEBUG=False)
    def test_command_refuses_to_run_when_debug_is_false(self):
        with patch.dict(
            os.environ,
            {"MEDCONNECT_DEMO_PASSWORD": "DemoCommandTest!2026"},
        ):
            with self.assertRaises(CommandError):
                call_command("seed_demo_users", stdout=StringIO())
