# MedConnect

MedConnect is a modular Django 5.2 LTS application using SQLite and Django Templates.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
```

## Development demo users

Set a development-only password and create the four demo accounts:

```powershell
$env:MEDCONNECT_DEMO_PASSWORD = "<development-password>"
python manage.py seed_demo_users
```

The command creates `admin_demo`, `doctor_demo`, `secretary_demo`, and `patient_demo`. It only runs when `DEBUG=True` and never grants staff or superuser status.

## Run

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/login/` and authenticate with a demo username and the configured password.

## Live updates

Open messaging threads receive new messages over Server-Sent Events. The
appointment request queue, cabinet agenda, and patient appointment list listen
for appointment changes and refresh automatically. The streams use Django's
`StreamingHttpResponse` and poll SQLite once per second; no message broker or
additional package is required.

Because SSE connections stay open, production deployments should use a server configuration that supports streaming responses and enough concurrent connections.

## Security boundary

Django superuser status is not authorization to access private medical records or messages. Future clinical modules must enforce their own explicit role and object-level permissions independently of `is_superuser`.

The original Product Backlog remains available in `MedConnect_Product_Backlog.pdf` and `docs/BACKLOG.md`.
