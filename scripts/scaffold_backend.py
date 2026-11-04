from pathlib import Path
import textwrap

ROOT = Path(r"D:\ENSIM\CustomerJourney\Microprojet_SI")
B = ROOT / "backend"
files = {}


def add(rel, content):
    files[str(B / rel)] = textwrap.dedent(content).strip("\n") + "\n"


# ------------------------------------------------------------------ manage.py
add("manage.py", r'''
    #!/usr/bin/env python
    import os
    import sys


    def main():
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)


    if __name__ == "__main__":
        main()
''')

add("requirements.txt", r'''
    django>=5.1
    djangorestframework>=3.15
    django-cors-headers>=4.4
    django-filter>=24.2
    channels>=4.0
    celery>=5.0
    redis>=5.0
    scikit-learn>=1.5
''')

add("requirements-ia.txt", r'''
    # Bonus (chatbot RAG) - a installer SEULEMENT si on y arrive :
    # uniquement des modeles open-source auto-heberges, aucun modele americain.
    -r requirements.txt
    sentence-transformers>=3.0
    pgvector-equivalent : sqlite-vec  (index vectoriel local)
''')

add(".env.example", r'''
    # Copier vers .env si besoin - aucun secret en dur dans le code
    SECRET_KEY=change-me-in-production
    DEBUG=1
    # Laisser vide pour tourner SANS Redis (fallback in-memory / synchrone)
    REDIS_URL=
''')

# ------------------------------------------------------------------- config
add("config/__init__.py", r'''
    try:
        from .celery import app as celery_app

        __all__ = ("celery_app",)
    except Exception:
        # Celery/Redis optionnel : le projet tourne sans (voir settings.CELERY_ENABLED)
        pass
''')

add("config/celery.py", r'''
    import os
    from celery import Celery

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    app = Celery("microprojet_si")
    app.config_from_object("django.conf:settings", namespace="CELERY")
    app.autodiscover_tasks()
''')

add("config/settings.py", r'''
    """Configuration unique - pensez a ne modifier ce fichier que de maniere ADDITIVE."""
    import os
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent.parent

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-a-changer")
    DEBUG = os.environ.get("DEBUG", "1") == "1"
    ALLOWED_HOSTS = ["*"] if DEBUG else [h for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h]

    INSTALLED_APPS = [
        # Django
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # Tiers
        "rest_framework",
        "corsheaders",
        "django_filters",
        # Applications metier (equipe : chaque membre est proprietaire d'un dossier)
        "apps.core",
        "apps.accounts",
        "apps.patients",
        "apps.agenda",
        "apps.messaging",
        "apps.segments",
        "apps.rgpd",
        "apps.dashboard",
        "apps.chatbot",
    ]

    try:
        import channels  # noqa: F401

        INSTALLED_APPS += ["channels"]
        CHANNELS_AVAILABLE = True
    except ImportError:
        CHANNELS_AVAILABLE = False

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        # RGPD : journalisation des acces (apps.rgpd)
        "apps.rgpd.middleware.AccessLogMiddleware",
    ]

    ROOT_URLCONF = "config.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [BASE_DIR / "templates"],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    WSGI_APPLICATION = "config.wsgi.application"
    ASGI_APPLICATION = "config.asgi.application"

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

    AUTH_USER_MODEL = "accounts.User"

    AUTH_PASSWORD_VALIDATORS = [
        {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

    LANGUAGE_CODE = "fr-fr"
    TIME_ZONE = "Europe/Paris"
    USE_I18N = True
    USE_TZ = True

    STATIC_URL = "static/"
    STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []
    MEDIA_URL = "media/"
    MEDIA_ROOT = BASE_DIR / "media"

    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    REST_FRAMEWORK = {
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.SessionAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
        "DEFAULT_FILTER_BACKENDS": [
            "django_filters.rest_framework.DjangoFilterBackend",
            "rest_framework.filters.SearchFilter",
            "rest_framework.filters.OrderingFilter",
        ],
        "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPagination",
        "PAGE_SIZE": 20,
    }

    # Frontend Next.js (dev)
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    CORS_ALLOW_CREDENTIALS = True

    # ---------------------------------------------------------------- temps reel
    # Sans Redis (defaut) : couche in-memory => la messagerie fonctionne en dev,
    # il suffit de poser REDIS_URL pour basculer sur Redis (voir CONTRIBUTING.md).
    REDIS_URL = os.environ.get("REDIS_URL", "")
    if REDIS_URL:
        try:
            import channels_redis  # noqa: F401

            CHANNEL_LAYERS = {
                "default": {
                    "BACKEND": "channels_redis.core.RedisChannelLayer",
                    "CONFIG": {"hosts": [REDIS_URL]},
                }
            }
        except ImportError:
            CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
    else:
        CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

    # ------------------------------------------------------------------- celery
    try:
        import celery  # noqa: F401

        CELERY_ENABLED = bool(REDIS_URL)
    except ImportError:
        CELERY_ENABLED = False
    CELERY_BROKER_URL = REDIS_URL or "memory://"
    CELERY_TASK_ALWAYS_EAGER = not CELERY_ENABLED

    # RGPD : politique de reglable via RegleRetention (apps.rgpd)
    RGPD_JOURNAL_RETENTION_DAYS = int(os.environ.get("RGPD_JOURNAL_RETENTION_DAYS", "365"))
''')

add("config/urls.py", r'''
    from django.contrib import admin
    from django.urls import include, path
    from rest_framework.decorators import api_view, permission_classes
    from rest_framework.permissions import AllowAny
    from rest_framework.response import Response

    @api_view(["GET"])
    @permission_classes([AllowAny])
    def health(request):
        return Response({"status": "ok", "service": "microprojet-si"})


    urlpatterns = [
        path("admin/", admin.site.urls),
        path("api/health/", health),
        path("api/auth/", include("apps.accounts.urls")),
        path("api/patients/", include("apps.patients.urls")),
        path("api/agenda/", include("apps.agenda.urls")),
        path("api/messagerie/", include("apps.messaging.urls")),
        path("api/segments/", include("apps.segments.urls")),
        path("api/rgpd/", include("apps.rgpd.urls")),
        path("api/dashboard/", include("apps.dashboard.urls")),
        path("api/chatbot/", include("apps.chatbot.urls")),
    ]
''')

add("config/asgi.py", r'''
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    from django.core.asgi import get_asgi_application

    django_asgi_app = get_asgi_application()

    try:
        from channels.auth import AuthMiddlewareStack
        from channels.routing import ProtocolTypeRouter, URLRouter

        from apps.messaging.routing import websocket_urlpatterns

        application = ProtocolTypeRouter(
            {
                "http": django_asgi_app,
                "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
            }
        )
    except ImportError:
        # channels non installe : on sert uniquement le HTTP
        application = django_asgi_app
''')

add("config/wsgi.py", r'''
    import os

    from django.core.wsgi import get_wsgi_application

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    application = get_wsgi_application()
''')

# --------------------------------------------------------------------- core
add("apps/__init__.py", "")
add("apps/core/__init__.py", "")
add("apps/core/apps.py", r'''
    from django.apps import AppConfig


    class CoreConfig(AppConfig):
        default_auto_field = "django.db.models.BigAutoField"
        name = "apps.core"
''')
add("apps/core/permissions.py", r'''
    """Permissions partagees - PROPRIETAIRE : Ahmed. Lecture seule pour les autres."""
    from rest_framework.permissions import BasePermission

    from apps.accounts.models import Role


    class IsMedecin(BasePermission):
        message = "Acces reserve au medecin."

        def has_permission(self, request, view):
            user = request.user
            return bool(user and user.is_authenticated and user.role == Role.MEDECIN)


    class IsMedecinOuSecretariat(BasePermission):
        message = "Acces reserve au cabinet (medecin ou secretariat)."

        def has_permission(self, request, view):
            user = request.user
            return bool(
                user and user.is_authenticated and user.role in (Role.MEDECIN, Role.SECRETARIAT)
            )


    class IsPatient(BasePermission):
        message = "Acces reserve aux patients."

        def has_permission(self, request, view):
            user = request.user
            return bool(user and user.is_authenticated and user.role == Role.PATIENT)


    class IsMedecinOuProprietaire(BasePermission):
        """Medecin/secretariat : acces total. Patient : acces a SES SEULES donnees."""

        message = "Vous ne pouvez acceder qu'a vos propres donnees."

        def has_permission(self, request, view):
            user = request.user
            return bool(user and user.is_authenticated)

        def has_object_permission(self, request, view, obj):
            user = request.user
            if user.role in (Role.MEDECIN, Role.SECRETARIAT):
                return True
            patient = getattr(user, "patient", None)
            if patient is None:
                return False
            return getattr(obj, "patient_id", None) == patient.id
''')

add("apps/core/pagination.py", r'''
    from rest_framework.pagination import PageNumberPagination


    class StandardPagination(PageNumberPagination):
        page_size = 20
        page_size_query_param = "page_size"
        max_page_size = 100
''')

add("apps/core/tasks.py", r'''
    """Point d'entree unique pour les taches planifiees.

    Sans Redis : la tache s'execute EN SYNCHRONE (le projet reste demontrable).
    Avec REDIS_URL : la tache part dans Celery.
    PROPRIETAIRE : Ahmed (utilise par Leonardo pour les rappels/relances).
    """
    from django.conf import settings


    def run_task(task, *args, **kwargs):
        if getattr(settings, "CELERY_ENABLED", False):
            return task.delay(*args, **kwargs)
        return task(*args, **kwargs)
''')

# ----------------------------------------------------------------- accounts
add("apps/accounts/__init__.py", "")
add("apps/accounts/apps.py", r'''
    from django.apps import AppConfig


    class AccountsConfig(AppConfig):
        default_auto_field = "django.db.models.BigAutoField"
        name = "apps.accounts"
''')
add("apps/accounts/models.py", r'''
    from django.contrib.auth.models import AbstractUser
    from django.db import models


    class Role(models.TextChoices):
        MEDECIN = "MEDECIN", "Medecin"
        SECRETARIAT = "SECRETARIAT", "Secretariat"
        PATIENT = "PATIENT", "Patient"


    class User(AbstractUser):
        role = models.CharField("role", max_length=20, choices=Role.choices, default=Role.PATIENT)
        telephone = models.CharField("telephone", max_length=20, blank=True)

        class Meta:
            verbose_name = "utilisateur"

        def __str__(self):
            return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
''')
add("apps/accounts/serializers.py", r'''
    from rest_framework import serializers

    from .models import User


    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = [
                "id",
                "username",
                "email",
                "first_name",
                "last_name",
                "role",
                "telephone",
            ]
            read_only_fields = ["id", "username"]
''')
add("apps/accounts/views.py", r'''
    from rest_framework import viewsets
    from rest_framework.decorators import action
    from rest_framework.permissions import IsAuthenticated
    from rest_framework.response import Response

    from apps.core.permissions import IsMedecin

    from .models import User
    from .serializers import UserSerializer


    class UserViewSet(viewsets.ReadOnlyModelViewSet):
        queryset = User.objects.all()
        serializer_class = UserSerializer
        permission_classes = [IsMedecin]
        search_fields = ["username", "first_name", "last_name", "email"]

        @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
        def me(self, request):
            return Response(UserSerializer(request.user).data)
''')
add("apps/accounts/urls.py", r'''
    from rest_framework.routers import DefaultRouter

    from .views import UserViewSet

    router = DefaultRouter()
    router.register("users", UserViewSet)

    urlpatterns = router.urls
''')
add("apps/accounts/admin.py", r'''
    from django.contrib import admin
    from django.contrib.auth.admin import UserAdmin

    from .models import User


    @admin.register(User)
    class CustomUserAdmin(UserAdmin):
        list_display = ("username", "first_name", "last_name", "role", "email", "is_active")
        list_filter = ("role", "is_active")
        fieldsets = UserAdmin.fieldsets + (("Supplement", {"fields": ("role", "telephone")}),)
''')

# ----------------------------------------------------------------- patients
add("apps/patients/__init__.py", "")
add("apps/patients/apps.py", r'''
    from django.apps import AppConfig


    class PatientsConfig(AppConfig):
        default_auto_field = "django.db.models.BigAutoField"
        name = "apps.patients"
''')
add("apps/patients/models.py", r'''
    from django.db import models

    from apps.accounts.models import User


    class Patient(models.Model):
        user = models.OneToOneField(
            User,
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name="patient",
            verbose_name="compte patient",
        )
        first_name = models.CharField("prenom", max_length=100)
        last_name = models.CharField("nom", max_length=100)
        email = models.EmailField("email", blank=True)
        telephone = models.CharField("telephone", max_length=20, blank=True)
        date_naissance = models.DateField("date de naissance", null=True, blank=True)
        adresse = models.CharField("adresse", max_length=255, blank=True)
        notes = models.TextField("notes administratives", blank=True)
        cree_le = models.DateTimeField("cree le", auto_now_add=True)
        modifie_le = models.DateTimeField("modifie le", auto_now=True)

        class Meta:
            ordering = ["last_name", "first_name"]
            verbose_name = "patient"

        @property
        def nom_complet(self):
            return f"{self.last_name} {self.first_name}".strip()

        def __str__(self):
            return self.nom_complet
''')
add("apps/patients/serializers.py", r'''
    from rest_framework import serializers

    from .models import Patient


    class PatientSerializer(serializers.ModelSerializer):
        nom_complet = serializers.ReadOnlyField()

        class Meta:
            model = Patient
            fields = [
                "id",
                "user",
                "nom_complet",
                "first_name",
                "last_name",
                "email",
                "telephone",
                "date_naissance",
                "adresse",
                "notes",
                "cree_le",
                "modifie_le",
            ]
            read_only_fields = ["id", "cree_le", "modifie_le"]
''')
add("apps/patients/views.py", r'''
    from rest_framework import viewsets
    from rest_framework.decorators import action
    from rest_framework.permissions import IsAuthenticated
    from rest_framework.response import Response

    from apps.core.permissions import IsMedecinOuSecretariat

    from .models import Patient
    from .serializers import PatientSerializer


    class PatientViewSet(viewsets.ModelViewSet):
        """CRUD des fiches patients - PROPRIETAIRE : Ahmed.

        US-05 a US-10 (voir docs/BACKLOG.md).
        """

        queryset = Patient.objects.all()
        serializer_class = PatientSerializer
        permission_classes = [IsMedecinOuSecretariat]
        search_fields = ["first_name", "last_name", "email", "telephone"]
        ordering_fields = ["last_name", "cree_le"]

        @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
        def me(self, request):
            patient = getattr(request.user, "patient", None)
            if patient is None:
                return Response({"detail": "Aucune fiche patient associee a ce compte."}, status=404)
            return Response(PatientSerializer(patient).data)
''')
add("apps/patients/urls.py", r'''
    from rest_framework.routers import DefaultRouter

    from .views import PatientViewSet

    router = DefaultRouter()
    router.register("patients", PatientViewSet)

    urlpatterns = router.urls
''')
add("apps/patients/admin.py", r'''
    from django.contrib import admin

    from .models import Patient


    @admin.register(Patient)
    class PatientAdmin(admin.ModelAdmin):
        list_display = ("last_name", "first_name", "email", "telephone", "cree_le")
        search_fields = ("last_name", "first_name", "email", "telephone")
''')

# ------------------------------------------------------------------- agenda
add("apps/agenda/__init__.py", "")
add("apps/agenda/apps.py", r'''
    from django.apps import AppConfig


    class AgendaConfig(AppConfig):
        default_auto_field = "django.db.models.BigAutoField"
        name = "apps.agenda"
''')
add("apps/agenda/models.py", r'''
    from django.db import models

    from apps.patients.models import Patient


    class AvailabilitySlot(models.Model):
        """Creneaux recurrents du medecin - PROPRIETAIRE : Leonardo (US-11)."""

        class Jour(models.TextChoices):
            LUNDI = "LUNDI", "Lundi"
            MARDI = "MARDI", "Mardi"
            MERCREDI = "MERCREDI", "Mercredi"
            JEUDI = "JEUDI", "Jeudi"
            VENDREDI = "VENDREDI", "Vendredi"
            SAMEDI = "SAMEDI", "Samedi"

        jour = models.CharField("jour", max_length=10, choices=Jour.choices)
        debut = models.TimeField("debut")
        fin = models.TimeField("fin")
        duree_par_defaut = models.PositiveIntegerField("duree par defaut (min)", default=30)
        actif = models.BooleanField("actif", default=True)

        class Meta:
            ordering = ["jour", "debut"]
            verbose_name = "creneau de disponibilite"

        def __str__(self):
            return f"{self.get_jour_display()} {self.debut}-{self.fin}"


    class Block(models.Model):
        """Indisponibilites ponctuelles (conges, pauses)."""

        date_debut = models.DateField("du")
        date_fin = models.DateField("au")
        motif = models.CharField("motif", max_length=200, blank=True)

        class Meta:
            ordering = ["date_debut"]
            verbose_name = "indisponibilite"

        def __str__(self):
            return f"{self.date_debut} -> {self.date_fin} {self.motif}".strip()


    class Appointment(models.Model):
        class Statut(models.TextChoices):
            PREVU = "PREVU", "Prevu"
            CONFIRME = "CONFIRME", "Confirme"
            ANNULE = "ANNULE", "Annule"
            TERMINE = "TERMINE", "Termine"
            ABSENTE = "ABSENTE", "Patient absent"

        patient = models.ForeignKey(
            Patient,
            on_delete=models.CASCADE,
            related_name="rendez_vous",
            verbose_name="patient",
        )
        debut = models.DateTimeField("debut")
        duree_minutes = models.PositiveIntegerField("duree (min)", default=30)
        motif = models.CharField("motif", max_length=200)
        statut = models.CharField("statut", max_length=20, choices=Statut.choices, default=Statut.PREVU)
        notes = models.TextField("notes", blank=True)
        rappel_envoye = models.BooleanField("rappel envoye", default=False)
        cree_le = models.DateTimeField(auto_now_add=True)
        modifie_le = models.DateTimeField(auto_now=True)

        class Meta:
            ordering = ["debut"]
            verbose_name = "rendez-vous"

        def __str__(self):
            return f"{self.patient} - {self.debut:%d/%m/%Y %H:%M}"
''')
add("apps/agenda/serializers.py", r'''
    from rest_framework import serializers

    from apps.patients.serializers import PatientSerializer

    from .models import Appointment, AvailabilitySlot, Block


    class AvailabilitySlotSerializer(serializers.ModelSerializer):
        class Meta:
            model = AvailabilitySlot
            fields = ["id", "jour", "debut", "fin", "duree_par_defaut", "actif"]


    class BlockSerializer(serializers.ModelSerializer):
        class Meta:
            model = Block
            fields = ["id", "date_debut", "date_fin", "motif"]


    class AppointmentSerializer(serializers.ModelSerializer):
        patient_nom = serializers.CharField(source="patient.nom_complet", read_only=True)

        class Meta:
            model = Appointment
            fields = [
                "id",
                "patient",
                "patient_nom",
                "debut",
                "duree_minutes",
                "motif",
                "statut",
                "notes",
                "rappel_envoye",
                "cree_le",
            ]
            read_only_fields = ["id", "rappel_envoye", "cree_le"]
''')
add("apps/agenda/views.py", r'''
    from rest_framework import viewsets

    from apps.accounts.models import Role
    from apps.core.permissions import IsMedecinOuProprietaire, IsMedecinOuSecretariat

    from .models import Appointment, AvailabilitySlot, Block
    from .serializers import AppointmentSerializer, AvailabilitySlotSerializer, BlockSerializer


    class AvailabilitySlotViewSet(viewsets.ModelViewSet):
        """PROPRIETAIRE : Leonardo (US-11)."""

        queryset = AvailabilitySlot.objects.all()
        serializer_class = AvailabilitySlotSerializer
        permission_classes = [IsMedecinOuSecretariat]


    class BlockViewSet(viewsets.ModelViewSet):
        queryset = Block.objects.all()
        serializer_class = BlockSerializer
        permission_classes = [IsMedecinOuSecretariat]


    class AppointmentViewSet(viewsets.ModelViewSet):
        """PROPRIETAIRE : Leonardo (US-12 a US-16).

        A FAIRE (Leonardo) :
        - filtrer les creneaux proposes selon AvailabilitySlot + Block
        - eviter les chevauchements a la creation
        - envoyer les rappels via apps.core.tasks.run_task
        """

        queryset = Appointment.objects.select_related("patient")
        serializer_class = AppointmentSerializer
        permission_classes = [IsMedecinOuProprietaire]
        filterset_fields = ["statut", "patient"]

        def get_queryset(self):
            qs = super().get_queryset()
            user = self.request.user
            if user.role == Role.PATIENT:
                patient = getattr(user, "patient", None)
                return qs.filter(patient=patient) if patient else qs.none()
            return qs
''')
add("apps/agenda/urls.py", r'''
    from rest_framework.routers import DefaultRouter

    from .views import AppointmentViewSet, AvailabilitySlotViewSet, BlockViewSet

    router = DefaultRouter()
    router.register("rendez-vous", AppointmentViewSet)
    router.register("disponibilites", AvailabilitySlotViewSet)
    router.register("indisponibilites", BlockViewSet)

    urlpatterns = router.urls
''')
add("apps/agenda/admin.py", r'''
    from django.contrib import admin

    from .models import Appointment, AvailabilitySlot, Block


    @admin.register(Appointment)
    class AppointmentAdmin(admin.ModelAdmin):
        list_display = ("patient", "debut", "motif", "statut", "rappel_envoye")
        list_filter = ("statut",)
        search_fields = ("patient__last_name", "patient__first_name", "motif")


    admin.site.register(AvailabilitySlot)
    admin.site.register(Block)
''')

# ---------------------------------------------------------------- messaging
add("apps/messaging/__init__.py", "")
add("apps/messaging/apps.py", r'''
    from django.apps import AppConfig


    class MessagingConfig(AppConfig):
        default_auto_field = "django.db.models.BigAutoField"
        name = "apps.messaging"
''')
add("apps/messaging/models.py", r'''
    from django.db import models

    from apps.accounts.models import User
    from apps.patients.models import Patient


    class Thread(models.Model):
        """Fil de discussion par patient - PROPRIETAIRE : Leonardo (US-17 a US-19)."""

        patient = models.ForeignKey(
            Patient, on_delete=models.CASCADE, related_name="conversations", verbose_name="patient"
        )
        sujet = models.CharField("sujet", max_length=200, blank=True)
        lu_par_cabinet = models.BooleanField("lu par le cabinet", default=False)
        cree_le = models.DateTimeField(auto_now_add=True)
        modifie_le = models.DateTimeField(auto_now=True)

        class Meta:
            ordering = ["-modifie_le"]
            verbose_name = "conversation"

        def __str__(self):
            return f"Conversation - {self.patient}"


    class Message(models.Model):
        thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")
        emetteur = models.ForeignKey(
            User, on_delete=models.CASCADE, related_name="messages_envoyes", verbose_name="emetteur"
        )
        corps = models.TextField("corps")
        piece_jointe = models.FileField("piece jointe", upload_to="messages/", blank=True, null=True)
        lu_le = models.DateTimeField("lu le", null=True, blank=True)
        cree_le = models.DateTimeField("envoye le", auto_now_add=True)

        class Meta:
            ordering = ["cree_le"]
            verbose_name = "message"

        def __str__(self):
            return f"Message de {self.emetteur} le {self.cree_le:%d/%m %H:%M}"
''')
add("apps/messaging/serializers.py", r'''
    from rest_framework import serializers

    from .models import Message, Thread


    class MessageSerializer(serializers.ModelSerializer):
        emetteur_nom = serializers.CharField(source="emetteur.get_full_name", read_only=True)

        class Meta:
            model = Message
            fields = ["id", "thread", "emetteur", "emetteur_nom", "corps", "piece_jointe", "lu_le", "cree_le"]
            read_only_fields = ["id", "emetteur", "lu_le", "cree_le"]


    class ThreadSerializer(serializers.ModelSerializer):
        messages = MessageSerializer(many=True, read_only=True)
        patient_nom = serializers.CharField(source="patient.nom_complet", read_only=True)

        class Meta:
            model = Thread
            fields = ["id", "patient", "patient_nom", "sujet", "lu_par_cabinet", "messages", "cree_le", "modifie_le"]
            read_only_fields = ["id", "lu_par_cabinet", "cree_le", "modifie_le"]
''')
add("apps/messaging/views.py", r'''
    from rest_framework import viewsets

    from apps.accounts.models import Role
    from apps.core.permissions import IsMedecinOuProprietaire, IsMedecinOuSecretariat

    from .models import Message, Thread
    from .serializers import MessageSerializer, ThreadSerializer


    class ThreadViewSet(viewsets.ModelViewSet):
        """PROPRIETAIRE : Leonardo (US-17 a US-19).

        A FAIRE (Leonardo) :
        - temps reel via MessagerieConsumer (voir consumers.py + routing.py)
        - marquer "non lu" a la reception, lu_le a la lecture
        - restriction : un patient ne voit QUE son propre fil
        """

        queryset = Thread.objects.select_related("patient")
        serializer_class = ThreadSerializer
        permission_classes = [IsMedecinOuProprietaire]

        def get_queryset(self):
            qs = super().get_queryset()
            user = self.request.user
            if user.role == Role.PATIENT:
                patient = getattr(user, "patient", None)
                return qs.filter(patient=patient) if patient else qs.none()
            return qs


    class MessageViewSet(viewsets.ModelViewSet):
        queryset = Message.objects.select_related("thread", "emetteur")
        serializer_class = MessageSerializer
        permission_classes = [IsMedecinOuSecretariat]

        def perform_create(self, serializer):
            # TODO Leonardo : emetteur = request.user, mise a jour de Thread.modifie_le
            serializer.save(emetteur=self.request.user)
''')
add("apps/messaging/routing.py", r'''
    """WebSockets - PROPRIETAIRE : Leonardo.

    Exemple : path("ws/messagerie/<int:thread_id>/", MessagerieConsumer.as_asgi())
    """
    websocket_urlpatterns = []
''')
add("apps/messaging/consumers.py", r'''
    """Consommateurs WebSockets - PROPRIETAIRE : Leonardo (US-17).

    Stub minimal : accepte la connexion et renvoie un echo.
    A completer : authentification (user connecte), controle d'appartenance au
    thread, persistance dans messaging.Message, diffusion au cabinet + patient.
    """
    from channels.generic.websocket import AsyncJsonWebsocketConsumer


    class MessagerieConsumer(AsyncJsonWebsocketConsumer):
        async def connect(self):
            await self.accept()

        async def receive_json(self, content, **kwargs):
            await self.send_json({"type": "echo", "payload": content})
''')
add("apps/messaging/urls.py", r'''
    from rest_framework.routers import DefaultRouter

    from .views import MessageViewSet, ThreadViewSet

    router = DefaultRouter()
    router.register("threads", ThreadViewSet)
    router.register("messages", MessageViewSet)

    urlpatterns = router.urls
''')
add("apps/messaging/admin.py", r'''
    from django.contrib import admin

    from .models import Message, Thread


    class MessageInline(admin.TabularInline):
        model = Message
        extra = 0


    @admin.register(Thread)
    class ThreadAdmin(admin.ModelAdmin):
        list_display = ("patient", "sujet", "lu_par_cabinet", "modifie_le")
        inlines = [MessageInline]
''')

# ----------------------------------------------------------------- segments
add("apps/segments/__init__.py", "")
add("apps/segments/apps.py", r'''
    from django.apps import AppConfig


    class SegmentsConfig(AppConfig):
        default_auto_field = "django.db.models.BigAutoField"
        name = "apps.segments"
''')
add("apps/segments/models.py", r'''
    from django.db import models

    from apps.patients.models import Patient


    class Segment(models.Model):
        """Groupe genere par le K-means - PROPRIETAIRE : Philippe (US-21 a US-25)."""

        nom = models.CharField("nom", max_length=100, unique=True)
        slug = models.SlugField("slug", unique=True)
        description = models.TextField("description", blank=True)
        centroid = models.JSONField("centroid", default=dict, blank=True)
        cree_le = models.DateTimeField(auto_now_add=True)

        class Meta:
            ordering = ["nom"]
            verbose_name = "segment"

        def __str__(self):
            return self.nom


    class SegmentAssignment(models.Model):
        patient = models.ForeignKey(
            Patient, on_delete=models.CASCADE, related_name="affectations", verbose_name="patient"
        )
        segment = models.ForeignKey(
            Segment, on_delete=models.CASCADE, related_name="affectations", verbose_name="segment"
        )
        actif = models.BooleanField("actif", default=True)
        affecte_le = models.DateTimeField(auto_now_add=True)

        class Meta:
            ordering = ["-affecte_le"]
            verbose_name = "affectation de segment"

        def __str__(self):
            return f"{self.patient} -> {self.segment}"


    class PatientScore(models.Model):
        """Score comportemental (0-100) recalcule par la tache de scoring."""

        patient = models.OneToOneField(
            Patient, on_delete=models.CASCADE, related_name="score", verbose_name="patient"
        )
        score = models.FloatField("score", default=0)
        facteurs = models.JSONField("facteurs", default=dict, blank=True)
        calcule_le = models.DateTimeField("calcule le", null=True, blank=True)

        class Meta:
            verbose_name = "score patient"

        def __str__(self):
            return f"{self.patient} : {self.score}"
''')
add("apps/segments/serializers.py", r'''
    from rest_framework import serializers

    from .models import PatientScore, Segment, SegmentAssignment


    class SegmentSerializer(serializers.ModelSerializer):
        nb_patients = serializers.SerializerMethodField()

        class Meta:
            model = Segment
            fields = ["id", "nom", "slug", "description", "centroid", "nb_patients", "cree_le"]

        def get_nb_patients(self, obj):
            return obj.affectations.filter(actif=True).count()


    class SegmentAssignmentSerializer(serializers.ModelSerializer):
        patient_nom = serializers.CharField(source="patient.nom_complet", read_only=True)
        segment_nom = serializers.CharField(source="segment.nom", read_only=True)

        class Meta:
            model = SegmentAssignment
            fields = ["id", "patient", "patient_nom", "segment", "segment_nom", "actif", "affecte_le"]


    class PatientScoreSerializer(serializers.ModelSerializer):
        patient_nom = serializers.CharField(source="patient.nom_complet", read_only=True)

        class Meta:
            model = PatientScore
            fields = ["id", "patient", "patient_nom", "score", "facteurs", "calcule_le"]
''')
add("apps/segments/views.py", r'''
    from rest_framework import viewsets
    from rest_framework.decorators import action
    from rest_framework.response import Response

    from apps.core.permissions import IsMedecinOuSecretariat

    from .models import PatientScore, Segment, SegmentAssignment
    from .serializers import PatientScoreSerializer, SegmentAssignmentSerializer, SegmentSerializer


    class SegmentViewSet(viewsets.ReadOnlyModelViewSet):
        """PROPRIETAIRE : Philippe (US-21 a US-25).

        A FAIRE (Philippe) : scikit-learn (K-means) + score comportemental,
        a declencher via l'action "recalculer". scikit-learn n'est importe QUE
        dans l'action : le reste du projet tourne sans lui.
        """

        queryset = Segment.objects.all()
        serializer_class = SegmentSerializer
        permission_classes = [IsMedecinOuSecretariat]
        lookup_field = "slug"

        @action(detail=False, methods=["post"])
        def recalculer(self, request):
            from django.utils import timezone

            # TODO Philippe : extraire les features, entrainer KMeans, ecrire
            # Segment + SegmentAssignment + PatientScore (US-21, US-22).
            return Response(
                {
                    "detail": "Non implemente (TODO Philippe - scikit-learn KMeans).",
                    "segments": Segment.objects.count(),
                    "scores": PatientScore.objects.count(),
                    "calcule_le": timezone.now(),
                },
                status=501,
            )


    class SegmentAssignmentViewSet(viewsets.ReadOnlyModelViewSet):
        queryset = SegmentAssignment.objects.select_related("patient", "segment")
        serializer_class = SegmentAssignmentSerializer
        permission_classes = [IsMedecinOuSecretariat]


    class PatientScoreViewSet(viewsets.ReadOnlyModelViewSet):
        queryset = PatientScore.objects.select_related("patient")
        serializer_class = PatientScoreSerializer
        permission_classes = [IsMedecinOuSecretariat]
''')
add("apps/segments/urls.py", r'''
    from rest_framework.routers import DefaultRouter

    from .views import PatientScoreViewSet, SegmentAssignmentViewSet, SegmentViewSet

    router = DefaultRouter()
    router.register("segments", SegmentViewSet)
    router.register("affectations", SegmentAssignmentViewSet)
    router.register("scores", PatientScoreViewSet)

    urlpatterns = router.urls
''')
add("apps/segments/admin.py", r'''
    from django.contrib import admin

    from .models import PatientScore, Segment, SegmentAssignment


    @admin.register(Segment)
    class SegmentAdmin(admin.ModelAdmin):
        list_display = ("nom", "slug", "cree_le")
        prepopulated_fields = {"slug": ("nom",)}


    admin.site.register(SegmentAssignment)
    admin.site.register(PatientScore)
''')

# -------------------------------------------------------------------- rgpd
add("apps/rgpd/__init__.py", "")
add("apps/rgpd/apps.py", r'''
    from django.apps import AppConfig


    class RgpdConfig(AppConfig):
        default_auto_field = "django.db.models.BigAutoField"
        name = "apps.rgpd"
''')
add("apps/rgpd/models.py", r'''
    from django.db import models

    from apps.accounts.models import User
    from apps.patients.models import Patient


    class Consentement(models.Model):
        """US-02 / US-38 - PROPRIETAIRE : Ahmed."""

        class Finalite(models.TextChoices):
            RDV = "RDV", "Prise de rendez-vous"
            MESSAGERIE = "MESSAGERIE", "Messagerie"
            ANALYSE = "ANALYSE", "Segmentation et scoring"
            CHATBOT = "CHATBOT", "Assistant conversationnel"

        patient = models.ForeignKey(
            Patient, on_delete=models.CASCADE, related_name="consentements", verbose_name="patient"
        )
        finalite = models.CharField("finalite", max_length=20, choices=Finalite.choices)
        accorde = models.BooleanField("accorde", default=False)
        donne_le = models.DateTimeField("donne le", auto_now_add=True)
        retire_le = models.DateTimeField("retire le", null=True, blank=True)
        version_texte = models.CharField("version du texte", max_length=20, default="v1")

        class Meta:
            ordering = ["-donne_le"]
            verbose_name = "consentement"
            constraints = [
                models.UniqueConstraint(
                    fields=["patient", "finalite", "version_texte"], name="unique_consentement"
                )
            ]

        def __str__(self):
            return f"{self.patient} / {self.get_finalite_display()} : {'oui' if self.accorde else 'non'}"


    class DemandeDonnee(models.Model):
        """US-34 / US-37 - droit a l'effacement et a la portabilite."""

        class Type(models.TextChoices):
            EXPORT = "EXPORT", "Export de mes donnees"
            EFFACEMENT = "EFFACEMENT", "Effacement de mes donnees"

        class Statut(models.TextChoices):
            EN_ATTENTE = "EN_ATTENTE", "En attente"
            TRAITEE = "TRAITEE", "Traitee"
            REFUSEE = "REFUSEE", "Refusee"

        patient = models.ForeignKey(
            Patient, on_delete=models.CASCADE, related_name="demandes_donnees", verbose_name="patient"
        )
        type = models.CharField("type", max_length=20, choices=Type.choices)
        statut = models.CharField(
            "statut", max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE
        )
        commentaire = models.TextField("commentaire", blank=True)
        demande_le = models.DateTimeField("demande le", auto_now_add=True)
        traite_le = models.DateTimeField("traite le", null=True, blank=True)

        class Meta:
            ordering = ["-demande_le"]
            verbose_name = "demande sur les donnees"

        def __str__(self):
            return f"{self.patient} - {self.get_type_display()} ({self.get_statut_display()})"


    class JournalAcces(models.Model):
        """US-36 - qui a vu quoi, quand (ecrit par AccessLogMiddleware)."""

        utilisateur = models.ForeignKey(
            User, on_delete=models.SET_NULL, null=True, blank=True, related_name="journal_acces"
        )
        action = models.CharField("action", max_length=255)
        chemin = models.CharField("chemin", max_length=255)
        adresse_ip = models.CharField("adresse IP", max_length=45, blank=True)
        date = models.DateTimeField("date", auto_now_add=True)

        class Meta:
            ordering = ["-date"]
            verbose_name = "journal d'acces"

        def __str__(self):
            return f"{self.date:%d/%m %H:%M} {self.action}"


    class RegleRetention(models.Model):
        """US-35 - purge automatique, parametree par l'administrateur."""

        modele = models.CharField("modele concerne", max_length=100, unique=True)
        jours = models.PositiveIntegerField("duree de conservation (jours)")
        description = models.CharField("description", max_length=255, blank=True)

        class Meta:
            verbose_name = "regle de retention"

        def __str__(self):
            return f"{self.modele} : {self.jours} jours"
''')
add("apps/rgpd/middleware.py", r'''
    """Journalisation des acces - PROPRIETAIRE : Ahmed (US-36).

    Ne logge que les utilisateurs connectes, hors fichiers statiques.
    Silencieux si la table n'existe pas encore (avant les migrations).
    """
    from .models import JournalAcces

    EXCLUDED_PREFIXES = ("/static/", "/media/", "/admin/jsi18n")
    EXCLUDED_SUBSTRINGS = ("/api/rgpd/journal",)


    def _client_ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")


    class AccessLogMiddleware:
        def __init__(self, get_response):
            self.get_response = get_response

        def __call__(self, request):
            response = self.get_response(request)
            try:
                user = getattr(request, "user", None)
                if user is None or not user.is_authenticated:
                    return response
                path = request.path
                if path.startswith(EXCLUDED_PREFIXES) or any(s in path for s in EXCLUDED_SUBSTRINGS):
                    return response
                JournalAcces.objects.create(
                    utilisateur=user,
                    action=request.method,
                    chemin=path,
                    adresse_ip=_client_ip(request),
                )
            except Exception:
                pass
            return response
''')
add("apps/rgpd/serializers.py", r'''
    from rest_framework import serializers

    from .models import Consentement, DemandeDonnee, JournalAcces, RegleRetention


    class ConsentementSerializer(serializers.ModelSerializer):
        class Meta:
            model = Consentement
            fields = [
                "id",
                "patient",
                "finalite",
                "accorde",
                "donne_le",
                "retire_le",
                "version_texte",
            ]
            read_only_fields = ["id", "donne_le", "retire_le"]


    class DemandeDonneeSerializer(serializers.ModelSerializer):
        class Meta:
            model = DemandeDonnee
            fields = [
                "id",
                "patient",
                "type",
                "statut",
                "commentaire",
                "demande_le",
                "traite_le",
            ]
            read_only_fields = ["id", "statut", "demande_le", "traite_le"]


    class JournalAccesSerializer(serializers.ModelSerializer):
        utilisateur_nom = serializers.CharField(source="utilisateur.__str__", read_only=True)

        class Meta:
            model = JournalAcces
            fields = ["id", "utilisateur", "utilisateur_nom", "action", "chemin", "adresse_ip", "date"]


    class RegleRetentionSerializer(serializers.ModelSerializer):
        class Meta:
            model = RegleRetention
            fields = ["id", "modele", "jours", "description"]
''')
add("apps/rgpd/views.py", r'''
    from rest_framework import viewsets
    from rest_framework.permissions import IsAuthenticated

    from apps.accounts.models import Role
    from apps.core.permissions import IsMedecin

    from .models import Consentement, DemandeDonnee, JournalAcces, RegleRetention
    from .serializers import (
        ConsentementSerializer,
        DemandeDonneeSerializer,
        JournalAccesSerializer,
        RegleRetentionSerializer,
    )


    class ConsentementViewSet(viewsets.ModelViewSet):
        """PROPRIETAIRE : Ahmed (US-02, US-38). Un patient ne voit que les siens."""

        serializer_class = ConsentementSerializer
        permission_classes = [IsAuthenticated]
        filterset_fields = ["finalite", "accorde"]

        def get_queryset(self):
            qs = Consentement.objects.select_related("patient")
            user = self.request.user
            if user.role == Role.PATIENT:
                patient = getattr(user, "patient", None)
                return qs.filter(patient=patient) if patient else qs.none()
            return qs

        def perform_create(self, serializer):
            user = self.request.user
            if user.role == Role.PATIENT:
                serializer.save(patient=getattr(user, "patient", None))
            else:
                serializer.save()


    class DemandeDonneeViewSet(viewsets.ModelViewSet):
        """US-34 / US-37 : le patient demande un export ou un effacement."""

        serializer_class = DemandeDonneeSerializer
        permission_classes = [IsAuthenticated]

        def get_queryset(self):
            qs = DemandeDonnee.objects.select_related("patient")
            user = self.request.user
            if user.role == Role.PATIENT:
                patient = getattr(user, "patient", None)
                return qs.filter(patient=patient) if patient else qs.none()
            return qs

        def perform_create(self, serializer):
            user = self.request.user
            if user.role == Role.PATIENT:
                serializer.save(patient=getattr(user, "patient", None))
            else:
                serializer.save()


    class JournalAccesViewSet(viewsets.ReadOnlyModelViewSet):
        """US-36 - consultation par le medecin uniquement."""

        queryset = JournalAcces.objects.select_related("utilisateur")
        serializer_class = JournalAccesSerializer
        permission_classes = [IsMedecin]


    class RegleRetentionViewSet(viewsets.ModelViewSet):
        queryset = RegleRetention.objects.all()
        serializer_class = RegleRetentionSerializer
        permission_classes = [IsMedecin]
''')
add("apps/rgpd/urls.py", r'''
    from rest_framework.routers import DefaultRouter

    from .views import ConsentementViewSet, DemandeDonneeViewSet, JournalAccesViewSet, RegleRetentionViewSet

    router = DefaultRouter()
    router.register("consentements", ConsentementViewSet)
    router.register("demandes", DemandeDonneeViewSet)
    router.register("journal", JournalAccesViewSet)
    router.register("retention", RegleRetentionViewSet)

    urlpatterns = router.urls
''')
add("apps/rgpd/admin.py", r'''
    from django.contrib import admin

    from .models import Consentement, DemandeDonnee, JournalAcces, RegleRetention


    admin.site.register(Consentement)
    admin.site.register(DemandeDonnee)
    admin.site.register(JournalAcces)
    admin.site.register(RegleRetention)
''')
add("apps/rgpd/management/__init__.py", "")
add("apps/rgpd/management/commands/__init__.py", "")
add("apps/rgpd/management/commands/purge_donnees.py", r'''
    """US-35 : purge automatique des donnees expirees.

    Lancer manuellement : python manage.py purge_donnees
    (ou via Celery beat quand REDIS_URL est configure).
    """
    from datetime import timedelta

    from django.core.management.base import BaseCommand
    from django.conf import settings
    from django.utils import timezone

    from apps.rgpd.models import JournalAcces, RegleRetention


    class Command(BaseCommand):
        help = "Applique la politique de retention (purge des donnees expirees)."

        def handle(self, *args, **options):
            regle = RegleRetention.objects.filter(modele="JournalAcces").first()
            jours = regle.jours if regle else settings.RGPD_JOURNAL_RETENTION_DAYS
            limite = timezone.now() - timedelta(days=jours)
            deleted, _ = JournalAcces.objects.filter(date__lt=limite).delete()
            self.stdout.write(
                self.style.SUCCESS(f"JournalAcces : {deleted} enregistrement(s) purge(s) (> {jours} jours).")
            )
''')

# ---------------------------------------------------------------- dashboard
add("apps/dashboard/__init__.py", "")
add("apps/dashboard/apps.py", r'''
    from django.apps import AppConfig


    class DashboardConfig(AppConfig):
        default_auto_field = "django.db.models.BigAutoField"
        name = "apps.dashboard"
''')
add("apps/dashboard/models.py", r'''
    # Pas de modele : le tableau de bord agrège les donnees des autres apps.
    # PROPRietaire : Philippe (US-40 a US-42).
''')
add("apps/dashboard/serializers.py", r'''
    from rest_framework import serializers


    class KpiSerializer(serializers.Serializer):
        patients_total = serializers.IntegerField()
        rendez_vous_jour = serializers.IntegerField()
        rendez_vous_a_venir = serializers.IntegerField()
        messages_non_lus = serializers.IntegerField()
        segments_total = serializers.IntegerField()
''')
add("apps/dashboard/views.py", r'''
    """US-40 a US-42 - PROPRIETAIRE : Philippe.

    KPIs de base deja calculs ; a enrichir (courbes, entonnoir, patients
    prioritaires combines au score - voir Segment/PatientScore).
    """
    from datetime import date

    from django.db.models import Count, Q
    from rest_framework.permissions import IsAuthenticated
    from rest_framework.response import Response
    from rest_framework.views import APIView

    from apps.agenda.models import Appointment
    from apps.core.permissions import IsMedecinOuSecretariat
    from apps.messaging.models import Thread
    from apps.patients.models import Patient
    from apps.segments.models import Segment


    class KpiView(APIView):
        permission_classes = [IsAuthenticated, IsMedecinOuSecretariat]

        def get(self, request):
            today = date.today()
            return Response(
                {
                    "patients_total": Patient.objects.count(),
                    "rendez_vous_jour": Appointment.objects.filter(
                        debut__date=today, statut__in=["PREVU", "CONFIRME"]
                    ).count(),
                    "rendez_vous_a_venir": Appointment.objects.filter(
                        debut__gt=timezone_now(), statut__in=["PREVU", "CONFIRME"]
                    ).count(),
                    "messages_non_lus": Thread.objects.filter(lu_par_cabinet=False).count(),
                    "segments_total": Segment.objects.count(),
                }
            )


    def timezone_now():
        from django.utils import timezone

        return timezone.now()
''')
add("apps/dashboard/urls.py", r'''
    from django.urls import path

    from .views import KpiView

    urlpatterns = [
        path("kpi/", KpiView.as_view(), name="dashboard-kpi"),
    ]
''')
add("apps/dashboard/admin.py", r'''
    # Pas de modele a administrer.
''')

# ----------------------------------------------------------------- chatbot
add("apps/chatbot/__init__.py", "")
add("apps/chatbot/apps.py", r'''
    from django.apps import AppConfig


    class ChatbotConfig(AppConfig):
        default_auto_field = "django.db.models.BigAutoField"
        name = "apps.chatbot"
''')
add("apps/chatbot/models.py", r'''
    from django.db import models

    from apps.patients.models import Patient


    class Document(models.Model):
        """Documents du cabinet indexes pour le RAG - BONUS (US-26)."""

        titre = models.CharField("titre", max_length=200)
        contenu = models.TextField("contenu")
        fichier = models.FileField("fichier", upload_to="documents/", blank=True, null=True)
        indexe_le = models.DateTimeField("indexe le", null=True, blank=True)
        cree_le = models.DateTimeField(auto_now_add=True)

        class Meta:
            ordering = ["titre"]
            verbose_name = "document du cabinet"

        def __str__(self):
            return self.titre


    class Conversation(models.Model):
        patient = models.ForeignKey(
            Patient,
            on_delete=models.CASCADE,
            related_name="conversations_chatbot",
            null=True,
            blank=True,
            verbose_name="patient",
        )
        cree_le = models.DateTimeField(auto_now_add=True)

        class Meta:
            ordering = ["-cree_le"]
            verbose_name = "conversation avec l'assistant"

        def __str__(self):
            return f"Conversation #{self.pk}"


    class MessageChat(models.Model):
        class Role(models.TextChoices):
            UTILISATEUR = "UTILISATEUR", "Utilisateur"
            ASSISTANT = "ASSISTANT", "Assistant"

        conversation = models.ForeignKey(
            Conversation, on_delete=models.CASCADE, related_name="messages"
        )
        role = models.CharField("role", max_length=20, choices=Role.choices)
        contenu = models.TextField("contenu")
        sources = models.JSONField("sources", default=list, blank=True)
        cree_le = models.DateTimeField(auto_now_add=True)

        class Meta:
            ordering = ["cree_le"]
            verbose_name = "message de l'assistant"

        def __str__(self):
            return f"{self.get_role_display()} : {self.contenu[:50]}"
''')
add("apps/chatbot/serializers.py", r'''
    from rest_framework import serializers

    from .models import Conversation, Document, MessageChat


    class DocumentSerializer(serializers.ModelSerializer):
        class Meta:
            model = Document
            fields = ["id", "titre", "contenu", "fichier", "indexe_le", "cree_le"]
            read_only_fields = ["id", "indexe_le", "cree_le"]


    class MessageChatSerializer(serializers.ModelSerializer):
        class Meta:
            model = MessageChat
            fields = ["id", "conversation", "role", "contenu", "sources", "cree_le"]
            read_only_fields = ["id", "role", "sources", "cree_le"]


    class AskSerializer(serializers.Serializer):
        question = serializers.CharField()
        conversation_id = serializers.IntegerField(required=False)
''')
add("apps/chatbot/views.py", r'''
    """BONUS (US-26 a US-30) - PROPRIETAIRE : Philippe.

    A FAIRE : embeddings locaux + sqlite-vec + LLM open-source auto-heberge
    (AUCUN modele americain, AUCUNE donnee sortante - voir CONTRIBUTING.md).
    """
    from rest_framework import viewsets
    from rest_framework.response import Response
    from rest_framework.views import APIView

    from apps.core.permissions import IsMedecinOuSecretariat

    from .models import Conversation, Document, MessageChat
    from .serializers import AskSerializer, DocumentSerializer, MessageChatSerializer


    class DocumentViewSet(viewsets.ModelViewSet):
        queryset = Document.objects.all()
        serializer_class = DocumentSerializer
        permission_classes = [IsMedecinOuSecretariat]


    class AskView(APIView):
        def post(self, request):
            serializer = AskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # TODO Philippe : retrieval sur Document, reponse generee en local
            # avec sources (US-27), puis tri de la demande (US-28).
            return Response(
                {
                    "detail": "RAG non implemente (bonus) - modele local a brancher.",
                    "question": serializer.validated_data["question"],
                    "reponse": None,
                    "sources": [],
                },
                status=501,
            )
''')
add("apps/chatbot/urls.py", r'''
    from rest_framework.routers import DefaultRouter
    from django.urls import path

    from .views import AskView, DocumentViewSet

    router = DefaultRouter()
    router.register("documents", DocumentViewSet)

    urlpatterns = router.urls + [
        path("ask/", AskView.as_view(), name="chatbot-ask"),
    ]
''')
add("apps/chatbot/admin.py", r'''
    from django.contrib import admin

    from .models import Conversation, Document, MessageChat


    admin.site.register(Document)
    admin.site.register(Conversation)
    admin.site.register(MessageChat)
''')

# ------------------------------------------------------------------- ecriture
for rel, content in files.items():
    path = Path(rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

print(f"{len(files)} fichiers ecrits dans {B}")
