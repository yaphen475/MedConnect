import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update development demo users"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("This command is only available when DEBUG=True.")

        password = os.environ.get("MEDCONNECT_DEMO_PASSWORD")
        if not password:
            raise CommandError("Set MEDCONNECT_DEMO_PASSWORD before running this command.")

        user_model = get_user_model()
        demo_users = (
            ("admin_demo", user_model.Role.ADMIN),
            ("doctor_demo", user_model.Role.DOCTOR),
            ("secretary_demo", user_model.Role.SECRETARY),
            ("patient_demo", user_model.Role.PATIENT),
        )

        for username, role in demo_users:
            user, created = user_model.objects.get_or_create(
                username=username,
                defaults={"role": role},
            )
            user.role = role
            user.is_active = True
            user.is_staff = False
            user.is_superuser = False
            user.set_password(password)
            user.save()
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} {username}")

        self.stdout.write(self.style.SUCCESS("Demo users are ready."))
