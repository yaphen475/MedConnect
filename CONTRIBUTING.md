# CONTRIBUTING — travailler en parallèle sans se marcher dessus

> Règle d'or : **chacun ne modifie que SES fichiers** (matrice ci-dessous).
> Tout le reste est en lecture seule — si vous avez besoin d'y toucher, annoncez-le d'abord au groupe.

## 0. Installation (une commande, pour tout le monde)

```powershell
git clone https://github.com/yaphen475/Microprojet_SI.git
cd Microprojet_SI
.\setup.cmd      # installe tout : venv, dependances, migrations, seed, npm install
.\dev.cmd        # demarre backend (:8000) + frontend (:3000) et ouvre le navigateur
```

Le script est **idempotent** : le relancer ne casse rien et ne réinstalle que ce qui manque.
Tests : `cd backend; .\.venv\Scripts\python.exe manage.py test tests`.
Base de démo à zéro : `.\setup.cmd -Reset`.

## 1. Matrice de propriété

| Membre | Dossiers / fichiers propriétaires | User stories |
|---|---|---|
| **Ahmed Trabelsi** | `backend/apps/core/`, `accounts/`, `patients/`, `rgpd/`, `config/settings.py`*, `config/urls.py`*, migrations de ces apps | US-01 → US-04, US-34 → US-39, RG-06, RG-08, RG-12 |
| **Leonardo Codeceira Goncalves Pinto** | `backend/apps/agenda/` (+ ses migrations) | US-05 → US-10, US-18 (innovation 1), RG-01 → RG-05 |
| **Philippe Henry Yap** | `backend/apps/dossiers/`, `chatbot/`, `segments/` (+ migrations) | US-11 → US-14, US-19 (innovation 2, bonus), US-20 (P3) |
| **Wissal Belhouane** | `frontend/**`, `backend/apps/messaging/`, `dashboard/` (+ migrations), maquettes **Figma** | US-15 → US-17, US-21, US-22 |

\* fichiers **partagés** : ouverture uniquement, et seulement en ajoutant (jamais en réécrivant).

**Interdits pour tous** (sauf accord du groupe) : `backend/apps/core/permissions.py` (Ahmed est propriétaire), les migrations des autres apps, `requirements.txt` (ajouts annoncés).

## 2. Branches et commits

```powershell
git checkout main
git pull
git checkout -b feat/ahmed-permissions        # feat/<prenom>-<sujet court>
# ... travailler, commit frequent ...
python manage.py check                        # obligatoire avant de rendre
git add .
git commit -m "feat(permissions): tests d acces secretariat sur les dossiers"
git push -u origin feat/ahmed-permissions
```

- Format de commit : `feat|fix|test|docs|chore(<app>): message en français`.
- **`main` reste toujours vert** : on ne merge que après `python manage.py check` sans erreur.
- Fusion en fin de séance (merge/review rapide en binôme, 10 min max).
- Si le pull signale un conflit sur un fichier **partagé** : on le résout à deux, pas en force-push.

## 3. Contrat d'API (pour avancer en parallèle)

Le frontend (Wissal) travaille sur les endpoints déjà montés — **ne changez pas
leur format sans le signaler**. Endpoints disponibles aujourd'hui :

| Endpoint | Propriétaire | Statut |
|---|---|---|
| `GET/POST /api/auth/users/`, `/api/auth/me/` | Ahmed | ✅ |
| `GET/POST /api/patients/patients/`, `/api/patients/patients/me/` | Ahmed | ✅ CRUD |
| `GET/POST /api/agenda/rendez-vous/`, `/disponibilites/`, `/indisponibilites/` | Leonardo | ✅ CRUD, workflow `statut` = EN_ATTENTE→CONFIRME/REFUSE à implémenter |
| `GET/POST /api/messagerie/threads/`, `/messages/` | Wissal | ✅ CRUD, filtré par participants |
| `GET/POST /api/dossiers/comptes-rendus/`, `/ordonnances/` | Philippe | ✅ CRUD, permissions par rôle |
| `GET /api/dashboard/kpi/` | Wissal/Philippe | ✅ KPIs de base |
| `GET/POST /api/rgpd/consentements/`, `/demandes/`, `/journal/`, `/retention/` | Ahmed | ✅ |
| `POST /api/segments/segments/recalculer/` | Philippe | ⏳ 501 (K-means à faire) |
| `POST /api/chatbot/ask/` | Philippe | ⏳ 501 (RAG bonus à faire) |
| `ws/messagerie/<thread_id>/` | Wissal | ⏳ stub (websocket) |

Tout **nouveau** endpoint : vous l'ajoutez dans l'app qui vous appartient + une ligne dans ce tableau.

## 4. Premières tâches de chacun (dès maintenant)

1. **Ahmed** — US-02 : écran/gestion des comptes avec rôle `ADMIN` (IsAdmin existe déjà) + **tests de non-acces** US-04 (la secrétaire ne doit pas lire un compte rendu, test automatique).
2. **Leonardo** — US-07 : `statut=EN_ATTENTE → CONFIRME` **par la secrétaire seulement** (RG-01), refus, et règle « un seul CONFIRME par créneau » (RG-05) + endpoint des créneaux libres calculés depuis `AvailabilitySlot` (US-18, innovation 1).
3. **Philippe** — US-11/US-12 : création de compte rendu par le médecin + test 403 pour la secrétaire ; puis US-13/US-14 ordonnances.
4. **Wissal** — frontend : `npm install` déjà prêt → écran de connexion avec choix de rôle + tableau de bord par profil (US-21/US-22) ; messagerie `lu_le`/non-lu (US-16) ; maquettes Figma.

## 5. Rappels du sujet

- **IA générative** : indiquer clairement les portions de code générées par IA.
- **IA souveraine** : aucun modèle américain, tout auto-hébergé, aucune donnée sortante.
- **Données fictives uniquement** ; documents « sans valeur médicale ».
- **7 h de TP** : le MVP est dans `docs/BACKLOG.md` §6 — ne jamais sacrifier le MVP pour le bonus (RAG).
