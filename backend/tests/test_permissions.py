"""Tests de permissions - les regles de gestion du backlog MedConnect.

Lancer :  python manage.py test tests
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.agenda.models import Appointment
from apps.dossiers.models import CompteRendu, Ordonnance
from apps.messaging.models import Message, Thread
from apps.patients.models import Patient


def creer_user(username, role, **extra):
    user = User.objects.create_user(username=username, password="test1234", role=role, **extra)
    return user


class BaseFixture(TestCase):
    """Un medecin, une secretaire, un admin, deux patients (dont un avec dossier)."""

    @classmethod
    def setUpTestData(cls):
        cls.medecin = creer_user("medecin", Role.MEDECIN, first_name="Claire", last_name="Fontaine")
        cls.secretaire = creer_user("secretaire", Role.SECRETARIAT, first_name="Martine", last_name="Roux")
        cls.admin = creer_user("admin", Role.ADMIN)
        cls.patient1 = creer_user("patient1", Role.PATIENT, first_name="Lucas", last_name="Bernard")
        cls.patient2 = creer_user("patient2", Role.PATIENT, first_name="Emma", last_name="Petit")
        cls.fiche1 = Patient.objects.create(
            user=cls.patient1, first_name="Lucas", last_name="Bernard", email="l1@example.fr"
        )
        cls.fiche2 = Patient.objects.create(
            user=cls.patient2, first_name="Emma", last_name="Petit", email="l2@example.fr"
        )
        cls.cr = CompteRendu.objects.create(
            patient=cls.fiche2, medecin=cls.medecin, date_consultation="2026-10-28",
            titre="Suivi", contenu="contenu medical secret",
        )
        cls.ord1 = Ordonnance.objects.create(
            patient=cls.fiche1, medecin=cls.medecin, contenu="ordonnance du patient 1"
        )
        cls.ord2 = Ordonnance.objects.create(
            patient=cls.fiche2, medecin=cls.medecin, contenu="ordonnance du patient 2"
        )


class TestPermissionsDossiers(BaseFixture):
    """RG-07, RG-09, RG-12 : les dossiers medicaux."""

    def setUp(self):
        self.client = APIClient()

    def test_medecin_accede_aux_comptes_rendus(self):
        self.client.force_authenticate(self.medecin)
        resp = self.client.get("/api/dossiers/comptes-rendus/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    def test_secretaire_interdite_aux_comptes_rendus(self):
        self.client.force_authenticate(self.secretaire)
        self.assertEqual(self.client.get("/api/dossiers/comptes-rendus/").status_code, 403)
        self.assertEqual(
            self.client.get(f"/api/dossiers/comptes-rendus/{self.cr.pk}/").status_code, 403
        )

    def test_admin_technique_interdit_aux_comptes_rendus(self):
        """RG-12 : l'admin technique n'a PAS acces aux donnees medicales."""
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.get("/api/dossiers/comptes-rendus/").status_code, 403)

    def test_secretaire_interdite_aux_ordonnances(self):
        self.client.force_authenticate(self.secretaire)
        self.assertEqual(self.client.get("/api/dossiers/ordonnances/").status_code, 403)

    def test_patient_ne_voit_que_ses_ordonnances(self):
        """RG-06 : patient1 ne voit jamais l'ordonnance du patient2."""
        self.client.force_authenticate(self.patient1)
        resp = self.client.get("/api/dossiers/ordonnances/")
        self.assertEqual(resp.status_code, 200)
        ids = [o["id"] for o in resp.data["results"]]
        self.assertEqual(ids, [self.ord1.pk])
        self.assertNotIn(self.ord2.pk, ids)

    def test_patient_ne_peut_pas_rediger_une_ordonnance(self):
        """RG-09 : seul le medecin redige."""
        self.client.force_authenticate(self.patient1)
        resp = self.client.post(
            "/api/dossiers/ordonnances/",
            {"patient": self.fiche1.pk, "contenu": "essai"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)


class TestPermissionsMessagerie(BaseFixture):
    """RG-11 : chaque utilisateur ne voit que SES conversations."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.thread_prive = Thread.objects.create(sujet="echange medecin/patient")
        cls.thread_prive.participants.set([cls.medecin, cls.patient1])
        cls.thread_autre = Thread.objects.create(sujet="autre echange")
        cls.thread_autre.participants.set([cls.medecin, cls.patient2])
        Message.objects.create(thread=cls.thread_prive, emetteur=cls.medecin, corps="secret")

    def setUp(self):
        self.client = APIClient()

    def test_patient1_ne_voit_que_son_fil(self):
        self.client.force_authenticate(self.patient1)
        ids = [t["id"] for t in self.client.get("/api/messagerie/threads/").data["results"]]
        self.assertEqual(ids, [self.thread_prive.pk])

    def test_secretaire_absente_des_fils_prives(self):
        """La secretaire ne participe a aucun fil : elle ne voit rien (RG-11)."""
        self.client.force_authenticate(self.secretaire)
        resp = self.client.get("/api/messagerie/threads/")
        self.assertEqual(resp.data["count"], 0)

    def test_admin_technique_sans_acces_au_contenu(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get("/api/messagerie/threads/")
        self.assertEqual(resp.data["count"], 0)


class TestWorkflowRendezVous(BaseFixture):
    """RG-01, RG-03 : statut initial + confirmation par la secretaire."""

    def test_une_demande_demarre_en_attente(self):
        rdv = Appointment.objects.create(
            patient=self.fiche1, debut="2026-11-10T09:00:00Z", motif="consultation"
        )
        self.assertEqual(rdv.statut, Appointment.Statut.EN_ATTENTE)

    def test_patient_ne_voit_que_ses_rendez_vous(self):
        Appointment.objects.create(patient=self.fiche1, debut="2026-11-10T09:00:00Z", motif="a")
        Appointment.objects.create(patient=self.fiche2, debut="2026-11-11T09:00:00Z", motif="b")
        self.client = APIClient()
        self.client.force_authenticate(self.patient1)
        resp = self.client.get("/api/agenda/rendez-vous/")
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["patient"], self.fiche1.pk)
