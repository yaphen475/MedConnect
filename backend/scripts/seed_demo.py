"""Jeu de donnees de DEMONSTRATION (fictives) pour MedConnect.

Lancer depuis backend/ :
    python scripts/seed_demo.py

Comptes crees (mot de passe commun : MedConnect2026!)
    admin       -> Administrateur (US-02)
    medecin     -> Dr. Claire Fontaine
    secretaire  -> Martine Roux (confirme les RDV - RG-01)
    patient1    -> Lucas Bernard
    patient2    -> Emma Petit
"""
import os
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.utils import timezone  # noqa: E402

from apps.accounts.models import Role, User  # noqa: E402
from apps.agenda.models import Appointment, AvailabilitySlot  # noqa: E402
from apps.chatbot.models import Document  # noqa: E402
from apps.dossiers.models import CompteRendu, Ordonnance  # noqa: E402
from apps.messaging.models import Message, Thread  # noqa: E402
from apps.patients.models import Patient  # noqa: E402
from apps.rgpd.models import Consentement  # noqa: E402

PASSWORD = "MedConnect2026!"


def user(username, first_name, last_name, role, email):
    obj, created = User.objects.get_or_create(
        username=username,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "role": role,
        },
    )
    if created:
        obj.set_password(PASSWORD)
        obj.save()
    return obj


def patient_account(username, first_name, last_name, email, telephone):
    compte = user(username, first_name, last_name, Role.PATIENT, email)
    profil, _ = Patient.objects.get_or_create(
        user=compte,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "telephone": telephone,
            "date_naissance": date(1990, 5, 12),
            "adresse": "12 rue des Lilas, 44000 Nantes",
        },
    )
    return profil


# ------------------------------------------------------------------ comptes
admin = user("admin", "Technique", "Admin", Role.ADMIN, "admin@medconnect.fr")
medecin = user("medecin", "Claire", "Fontaine", Role.MEDECIN, "dr.fontaine@medconnect.fr")
secretaire = user("secretaire", "Martine", "Roux", Role.SECRETARIAT, "secretariat@medconnect.fr")
p1 = patient_account("patient1", "Lucas", "Bernard", "lucas.bernard@example.fr", "0611223344")
p2 = patient_account("patient2", "Emma", "Petit", "emma.petit@example.fr", "0655667788")

# ------------------------------------------------------- dispos du medecin
for jour, debut, fin in [
    ("LUNDI", time(8, 30), time(12, 0)),
    ("LUNDI", time(14, 0), time(18, 0)),
    ("MARDI", time(8, 30), time(12, 0)),
    ("MERCREDI", time(14, 0), time(18, 0)),
    ("JEUDI", time(8, 30), time(12, 0)),
    ("VENDREDI", time(9, 0), time(13, 0)),
]:
    AvailabilitySlot.objects.get_or_create(jour=jour, debut=debut, fin=fin)

# ----------------------------------------------------------------- RDV
now = timezone.now()


def rdv(patient, offset_days, hour, motif, statut, duree=30):
    debut = timezone.make_aware(datetime.combine(date.today() + timedelta(days=offset_days), time(hour, 0)))
    obj, _ = Appointment.objects.get_or_create(
        patient=patient, debut=debut, motif=motif,
        defaults={"statut": statut, "duree_minutes": duree},
    )
    return obj


demande = rdv(p1, 3, 9, "Consultation generale - demande en ligne", Appointment.Statut.EN_ATTENTE)
confirme = rdv(p2, 2, 14, "Suivi tension", Appointment.Statut.CONFIRME)
passe = rdv(p2, -7, 10, "Douleurs lombaires", Appointment.Statut.TERMINE)

# ------------------------------------------------------- dossier medical
CompteRendu.objects.get_or_create(
    patient=p2, date_consultation=date.today() - timedelta(days=7),
    titre="Consultation de suivi",
    defaults={
        "medecin": medecin,
        "contenu": (
            "Patient asymptomatique. TA 132/84. Examen clinique normal. "
            "Conseil hygieno-dietetique. Controle dans 3 mois. "
            "[DEMONSTRATION - aucune valeur medicale]"
        ),
    },
)
Ordonnance.objects.get_or_create(
    patient=p2,
    defaults={
        "medecin": medecin,
        "contenu": "1. Mesure de la tension 2x/semaine\n2. Reprise progressive du sport\n[DEMONSTRATION - aucune valeur medicale]",
    },
)

# ------------------------------------------------------------- messagerie
t1, _ = Thread.objects.get_or_create(sujet="Question administrative")
t1.participants.set([medecin, secretaire, p1.user])
if not t1.messages.exists():
    Message.objects.create(thread=t1, emetteur=p1.user, corps="Bonjour, puis-je changer mon rendez-vous de mardi ?")
    Message.objects.create(thread=t1, emetteur=secretaire, corps="Bonjour, oui, je vous propose jeudi 9h. Dites-moi si cela vous convient.")

t2, _ = Thread.objects.get_or_create(sujet="Echanges medecin / patient")
t2.participants.set([medecin, p2.user])
if not t2.messages.exists():
    Message.objects.create(thread=t2, emetteur=medecin, corps="Bonjour Madame Petit, pensez a jeuner 8h avant l'examen.")
    Message.objects.create(thread=t2, emetteur=p2.user, corps="Merci Docteur, c'est noté.")

# --------------------------------------------------- consentements RGPD
for profil in (p1, p2):
    for finalite in ["RDV", "MESSAGERIE", "ANALYSE", "CHATBOT"]:
        Consentement.objects.get_or_create(
            patient=profil, finalite=finalite, version_texte="v1",
            defaults={"accorde": finalite in ("RDV", "MESSAGERIE")},
        )

# ------------------------------------- base documentaire du chatbot (bonus)
for titre, contenu in [
    (
        "Horaires du cabinet",
        "Le cabinet ouvre du lundi au vendredi. Matin : 8h30-12h00. "
        "Apres-midi : 14h00-18h00 (lundi et mardi), 14h00-18h00 le mercredi, "
        "8h30-12h00 le jeudi, 9h00-13h00 le vendredi.",
    ),
    (
        "Comment demander un rendez-vous",
        "Connectez-vous a votre espace patient, ouvrez l'onglet Disponibilites, "
        "choisissez un creneau libre puis envoyez votre demande. "
        "La secretaire confirme ou refuse la demande ; vous etes informe de l'etat dans votre espace.",
    ),
    (
        "Comment retrouver mes ordonnances",
        "Depuis votre espace patient, l'onglet Ordonnances affiche uniquement vos "
        "propres ordonnances. Vous pouvez aussi les demander a la secretaire.",
    ),
    (
        "Contacter le cabinet",
        "Utilisez la messagerie interne depuis votre espace, ou telephonez au 02 00 00 00 00. "
        "En cas d'urgence vitale, composez le 15.",
    ),
]:
    Document.objects.get_or_create(titre=titre, defaults={"contenu": contenu})

print("=" * 60)
print("MedConnect - donnees de demonstration pretes.")
print(f"Mot de passe commun : {PASSWORD}")
for compte in (admin, medecin, secretaire, p1.user, p2.user):
    print(f"  - {compte.username:12} ({compte.get_role_display()})")
print(f"Demandes en attente : {Appointment.objects.filter(statut='EN_ATTENTE').count()}")
print("=" * 60)
