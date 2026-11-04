# MedConnect — Micro-projet SI (4A INFO, ENSIM)

Application web de gestion pour un cabinet médical privé : agenda, patients,
dossiers médicaux, messagerie et assistant RAG — avec des contrôles d'accès
stricts par rôle (RGPD, données fictives uniquement).

**Référence backlog :** [`docs/BACKLOG.md`](docs/BACKLOG.md) (Product Backlog MedConnect)
**Règles d'équipe et répartition :** [`CONTRIBUTING.md`](CONTRIBUTING.md)

## Démarrage — 2 commandes (`make`)

```bash
make setup    # 1 fois : venv + pip + migrations + seed + npm install
make start    # backend (:8000) + frontend (:3000), ouvre le navigateur
```

Toutes les commandes (`make help`) :

| Commande | Rôle |
|---|---|
| `make setup` | installe tout — **idempotent**, à relancer quand besoin |
| `make start` | démarre les deux serveurs (`make start BROWSER_OPEN=0` sans navigateur) |
| `make stop` | arrête les deux serveurs (cible uniquement les ports 8000/3000) |
| `make test` | lance les tests Django |
| `make reset` | base de démo à zéro (puis `make seed`) |
| `make health` / `make logs` | vérifie / affiche l'état des serveurs |

> **Installation de make (une fois)** — Windows : `scoop install make`
> (sinon `winget install GnuWin32.Make`). Git for Windows est requis :
> il fournit le `sh` utilisé par le Makefile.
>
> Sans make : `.\setup.cmd` puis `.\dev.cmd` — ou
> `bash setup.sh [--start] [--stop] [--test] [--reset]` sous WSL/macOS/Linux.

Équivalent manuel, si vous préférez :

```powershell
# 1. Backend (dans backend/)
python -m pip install -r requirements.txt
python manage.py migrate
python scripts/seed_demo.py          # donnees de demonstration
python manage.py runserver           # API sur http://localhost:8000

# 2. Frontend (dans frontend/, autre terminal)
npm install
npm run dev                          # UI sur http://localhost:3000
```

**Comptes de démo** (mot de passe : `MedConnect2026!`) :

| Login | Rôle |
|---|---|
| `admin` | Administrateur technique |
| `medecin` | Dr. Claire Fontaine |
| `secretaire` | Martine Roux (seule à pouvoir confirmer un RDV — RG-01) |
| `patient1` | Lucas Bernard |
| `patient2` | Emma Petit |

## Structure

```
Microprojet_SI/
├── backend/                  # Django + DRF (API REST /api/...)
│   ├── config/               # settings, urls, asgi, celery
│   └── apps/
│       ├── core/             # permissions partagees, pagination, tasks  [Ahmed]
│       ├── accounts/         # User + roles (ADMIN/MEDECIN/SECRETARIAT/PATIENT) [Ahmed]
│       ├── patients/         # fiches patients                            [Ahmed]
│       ├── rgpd/             # consentements, journal, retention, purge   [Ahmed]
│       ├── agenda/           # dispos, demandes/RDV workflow              [Leonardo]
│       ├── dossiers/         # comptes rendus + ordonnances               [Philippe]
│       ├── messaging/        # threads + messages (participants only)     [Wissal]
│       ├── segments/         # scoring / K-means (US-20, P3 - reserve)    [Philippe]
│       ├── dashboard/        # KPIs par profil                            [Wissal + Philippe]
│       └── chatbot/          # assistant RAG (US-19, bonus)               [Philippe]
├── frontend/                 # Next.js (UI, maquettes Figma, accessibilite) [Wissal]
├── docs/                     # BACKLOG, architecture, notes d'equipe
└── scripts/                  # scaffold, seed
```

## Contraintes non négociables (rappel)

- **Données 100 % fictives** — aucun vrai patient, aucune valeur médicale.
- **Aucun modèle d'IA américain** : LLM/embeddings open-source auto-hébergés uniquement, aucune donnée sortante.
- **RGPD** : droit à l'effacement (`python manage.py purge_donnees`), journal des accès, consentements.
- **Accessibilité RGAA / WCAG 2.1 AA** (navigation clavier, contrastes, lecteurs d'écran).
- **Code généré par IA : le signaler clairement** dans les commits et le code (consigne du sujet).
