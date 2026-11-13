"""Documentary base of the assistant (US-19).

A small, explicit knowledge base: the retrieval module (see ``retrieval.py``)
picks the documents that best match the question — a lightweight
Retrieval-Augmented Generation approach, fully offline and deterministic.

Titles and contents are lazy-translated: the active request language decides
whether the French source or the English catalogue is served. Tags stay
language-neutral lists of keywords (French + English) because they feed the
retrieval scoring, not the display.
"""

from django.utils.translation import gettext_lazy as _

DOCS = [
    {
        "id": "horaires",
        "title": _("Horaires du cabinet"),
        "tags": [
            "horaire",
            "horaires",
            "ouverture",
            "ouvert",
            "ferme",
            "fermeture",
            "quand",
            "plage",
            "creneau",
            "hours",
            "opening",
            "open",
            "closed",
            "closure",
            "when",
        ],
        "content": _(
            "Le cabinet est ouvert du lundi au vendredi, de 9h00 a 17h00. "
            "Les rendez-vous sont proposés par créneaux de 30 minutes. "
            "Le cabinet est fermé le samedi et le dimanche."
        ),
    },
    {
        "id": "demande-rdv",
        "title": _("Demander un rendez-vous"),
        "tags": [
            "rendez-vous",
            "rdv",
            "demande",
            "demander",
            "creneau",
            "reserve",
            "reserver",
            "disponibilite",
            "disponible",
            "prendre",
            "appointment",
            "request",
            "booking",
            "book",
            "slot",
            "available",
            "availability",
        ],
        "content": _(
            "Connectez-vous à votre espace patient puis ouvrez "
            "« Request an appointment ». Les créneaux libres sont détectés "
            "automatiquement : choisissez un créneau et envoyez votre demande. "
            "Votre demande reste « En attente » : seule la secrétaire la "
            "confirme. Une demande n'est pas une réservation définitive."
        ),
    },
    {
        "id": "suivi-rdv",
        "title": _("Suivre mes demandes et rendez-vous"),
        "tags": [
            "suivi",
            "etat",
            "statut",
            "confirme",
            "refuse",
            "attente",
            "mes-rendez-vous",
            "annule",
            "status",
            "track",
            "follow",
            "pending",
            "confirmed",
            "refused",
            "cancelled",
        ],
        "content": _(
            "Ouvrez « My appointments » : chaque demande affiche son statut "
            "(En attente, Confirmé, Refusé ou Annulé). Une confirmation ou un "
            "refus apparaît automatiquement dans votre espace personnel."
        ),
    },
    {
        "id": "ordonnances",
        "title": _("Retrouver mes ordonnances"),
        "tags": [
            "ordonnance",
            "ordonnances",
            "prescription",
            "prescriptions",
            "medicament",
            "traits",
            "find",
            "retrieve",
            "medication",
        ],
        "content": _(
            "Depuis votre espace patient, ouvrez « My prescriptions » : vous "
            "voyez uniquement vos propres ordonnances, datées et signées par "
            "votre médecin. Les documents présentés sont des démonstrations "
            "sans valeur médicale. Votre médecin rédige une nouvelle "
            "ordonnance depuis l'espace Prescriptions."
        ),
    },
    {
        "id": "comptes-rendus",
        "title": _("Comptes rendus de consultation"),
        "tags": [
            "compte-rendu",
            "comptes-rendus",
            "consultation",
            "historique",
            "medical",
            "dossier",
            "report",
            "reports",
            "records",
            "history",
        ],
        "content": _(
            "Le médecin rédige un compte rendu après chaque consultation : il "
            "est enregistré dans l'historique du patient, présenté de manière "
            "chronologique. Seul le médecin y accède : la secrétaire et "
            "l'administrateur technique n'ont aucun accès aux données "
            "médicales."
        ),
    },
    {
        "id": "contacter-secretaire",
        "title": _("Contacter la secrétaire"),
        "tags": [
            "contacter",
            "contact",
            "secretaire",
            "messagerie",
            "message",
            "ecrire",
            "joindre",
            "messaging",
            "write",
            "reach",
            "secretary",
        ],
        "content": _(
            "Utilisez la messagerie interne : ouvrez « New message », "
            "sélectionnez la secrétaire et envoyez votre message. La "
            "secrétaire reçoit votre message et vous répond dans le même fil. "
            "Seuls les participants d'une conversation peuvent la lire."
        ),
    },
    {
        "id": "confidentialite",
        "title": _("Confidentialité et rôles"),
        "tags": [
            "confidentialite",
            "donnees",
            "rgpd",
            "securite",
            "mot-de-passe",
            "acces",
            "role",
            "roles",
            "administrateur",
            "privacy",
            "data",
            "security",
            "access",
            "password",
        ],
        "content": _(
            "Chaque profil accède uniquement à ses droits : le médecin aux "
            "données médicales, la secrétaire aux données administratives, le "
            "patient à ses propres informations. L'administrateur technique "
            "gère les comptes mais n'a aucun accès automatique aux données "
            "médicales ni au contenu des messages."
        ),
    },
    {
        "id": "confirmation",
        "title": _("Confirmation et annulation"),
        "tags": [
            "confirmer",
            "confirmation",
            "annuler",
            "annulation",
            "refuser",
            "refus",
            "validation",
            "confirm",
            "cancel",
            "cancellation",
            "refusal",
        ],
        "content": _(
            "Seule la secrétaire confirme ou refuse une demande de rendez-vous. "
            "Un rendez-vous confirmé rend son créneau indisponible et "
            "un créneau ne peut accueillir qu'un seul rendez-vous confirmé. "
            "Annuler un rendez-vous confirmé rend le créneau à nouveau libre."
        ),
    },
]

REFUSAL = _(
    "Je ne peux pas répondre à cette question : l'assistant ne fournit "
    "jamais de diagnostic, de conseil médical ni de prescription. "
    "Pour un avis médical, contactez votre médecin ou la "
    "secrétaire du cabinet."
)

FALLBACK = _(
    "Je n'ai pas trouvé de document correspondant à votre question. Essayez "
    "par exemple : « Quels sont les horaires d'ouverture ? », « Comment "
    "demander un rendez-vous ? », « Comment retrouver mes ordonnances ? » "
    "ou « Comment contacter la secrétaire ? »."
)

INTRO = _(
    "D'après la base documentaire du cabinet, voici l'information utile :"
)
