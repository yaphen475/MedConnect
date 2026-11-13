# MedConnect — Functional modules (US-03 → US-19)

This document maps the modules implemented on top of the authentication /
dashboard base (US-01, US-22) delivered in commit `5402eb1`.

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
$env:MEDCONNECT_DEMO_PASSWORD = "MedConnect2026!"
python manage.py seed_demo_users
python manage.py runserver
```

Demo accounts: `admin_demo`, `doctor_demo`, `secretary_demo`, `patient_demo`
(password above, development only).

Run the whole test suite (72 tests, includes the accounts suite):

```powershell
python manage.py test
```

## Module map

| Module | URL | Roles | Backlog |
|---|---|---|---|
| Patient files | `/patients/` | Doctor, Secretary (Patient → own file) | US-03, US-04, RG-06/07/08/12 |
| Available slots | `/agenda/slots/` | Patient | US-05, US-06, US-18 (Innovation 1) |
| My appointments | `/agenda/my/` | Patient | US-09, US-10 |
| Appointment requests | `/agenda/requests/` | Secretary | US-07, RG-01/03/04/05 |
| Cabinet schedule | `/agenda/` | Doctor, Secretary | US-08, US-09 |
| Medical reports | `/dossiers/` | Doctor, Patient (own) | US-11, US-12, RG-07/09/10 |
| Patient history | `/dossiers/patient/<id>/` | Doctor | US-12 |
| Prescriptions | `/dossiers/prescriptions/` | Doctor, Patient (own) | US-13, US-14 |
| Messaging | `/messaging/` | Doctor, Secretary, Patient (admin excluded) | US-15, US-16, US-17, RG-11/12 |
| Assistant (RAG) | `/chatbot/` | Everyone | US-19, RG-13 |

## Architecture

* `apps/core/permissions.py` — shared `role_required()` decorator
  (plain helper package, **not** in `INSTALLED_APPS`, so no shared config
  file has to be modified).
* `apps/<module>/` — models, forms, views, urls, tests (namespace per app,
  already wired in `config/urls.py`).
* `templates/modules/layout.html` — module layout: extends
  `accounts/base.html` and reuses `accounts.css`, adds a role-aware sidebar
  with real links between modules. **No teammate-owned file was modified.**
* `static/css/modules.css` — supplement styles (tables, slots grid, chat
  bubbles).

## Enforced business rules

* RG-01: only the secretary confirms/refuses an appointment.
* RG-02/03: a patient only requests a free slot; status starts « En attente ».
* RG-04/05: conditional unique constraint
  (`agenda_confirmed_slot_unique`) + atomic check → a slot can never host two
  confirmed appointments; pending requests do not lock a slot.
* RG-06: a patient only accesses his own data.
* RG-07/09: medical fields, reports and prescriptions are doctor-only.
* RG-11: only conversation participants read a thread.
* RG-12: the technical administrator has no access to patient data, medical
  records or message content (403).
* RG-13: the assistant refuses diagnostic questions and displays its sources.

## Known integration point (for the team)

The dashboard cards still show « Coming soon » because
`apps/accounts/tests.py::test_dashboard_navigation_matches_user_role`
asserts that exact text. To connect the dashboard to the modules, the owner
of `apps/accounts` can add a `"url"` key to `ROLE_NAVIGATION` and use it in
`templates/accounts/dashboard.html` (and update the test). Every module URL
is already reserved and stable, as listed in the table above.
