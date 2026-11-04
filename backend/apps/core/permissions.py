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


class IsAdmin(BasePermission):
    message = "Acces reserve a l'administrateur technique."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == Role.ADMIN)


class IsMedecinOuPatientProprietaire(BasePermission):
    """Dossiers medicaux (RG-07, RG-09) :
    - medecin : lecture/ecriture integrale
    - patient : lecture de SES SEULES ordonnances
    - secretariat et admin technique : AUCUN acces
    """

    message = "Acces interdit a ces donnees medicales."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role in (Role.MEDECIN, Role.PATIENT))

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == Role.MEDECIN:
            return True
        patient = getattr(user, "patient", None)
        if patient is None:
            return False
        return getattr(obj, "patient_id", None) == patient.id
