# Consultation Management System

A production-ready **mini Consultation Management System** built with Django REST Framework and Bootstrap 5, featuring AI-powered consultation summaries via OpenAI (with a mock fallback).

---

## Features

| Feature | Details |
|---|---|
| Patient management | Create & list patients |
| Consultation management | Create & list consultations, filter by patient |
| AI Summary | Generate structured clinical summaries via OpenAI (or mock) |
| Pagination | 10 items per page across all list endpoints |
| Search & Ordering | Query params on all list endpoints |
| JWT Authentication | Token-based auth (endpoints are open by default, easy to lock down) |
| Swagger / ReDoc | Interactive API docs at `/swagger/` and `/redoc/` |
| Unit Tests | pytest-django test suite for both apps |
| Docker | One-command `docker-compose up` |

---

## Project Structure

```
task_2/
├── backend/                  # Django project
│   ├── consultation_system/  # Project config (settings, urls, exception_handler)
│   ├── patients/             # Patient app (model, serializer, views, tests)
│   ├── consultations/        # Consultation app (model, serializer, views, tests)
│   │   └── services/
│   │       └── ai_service.py # AI summary service (OpenAI + mock)
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   └── index.html            # Single-page Bootstrap 5 frontend
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Prerequisites

- Python 3.10+ and `pip`
- (Optional) Docker & docker-compose for containerised setup
- (Optional) An OpenAI API key for real AI summaries

---

## Local Setup (without Docker)

### 1. Clone & create virtual environment

```bash
git clone <your-repo-url>
cd task_2

python3 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate.bat     # Windows
```

### 2. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set SECRET_KEY (required) and optionally OPENAI_API_KEY
```

> **Note**: If `OPENAI_API_KEY` is not set, the AI summary endpoint will return a realistic mock response — no API account needed to try the system.

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. (Optional) Create a superuser for Django admin

```bash
python manage.py createsuperuser
```

### 6. Start the backend

```bash
python manage.py runserver
# API available at http://localhost:8000
```

### 7. Open the frontend

Open `frontend/index.html` in your browser, **or** serve it:

```bash
cd ../frontend
python3 -m http.server 5500
# Open http://localhost:5500
```

---

## Docker Setup

```bash
# Copy and fill in the env file first
cp backend/.env.example backend/.env

# Build and start both services
docker-compose up --build

# Backend:  http://localhost:8000
# Frontend: http://localhost:5500
# Swagger:  http://localhost:8000/swagger/
```

To run migrations inside Docker:

```bash
docker-compose exec backend python manage.py migrate
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/patients/` | List all patients (paginated) |
| `POST` | `/api/patients/` | Create a patient |
| `GET` | `/api/consultations/` | List consultations (paginated, filterable) |
| `POST` | `/api/consultations/` | Create a consultation |
| `POST` | `/api/consultations/{id}/generate-summary/` | Generate AI summary |
| `POST` | `/api/auth/token/` | Obtain JWT access & refresh tokens |
| `POST` | `/api/auth/token/refresh/` | Refresh JWT access token |
| `GET` | `/swagger/` | Swagger UI |
| `GET` | `/redoc/` | ReDoc documentation |

### Filtering & Pagination

```bash
# Filter consultations by patient
GET /api/consultations/?patient=1

# Search patients
GET /api/patients/?search=jane

# Pagination
GET /api/consultations/?page=2
```

### Example Requests

```bash
# Create a patient
curl -X POST http://localhost:8000/api/patients/ \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Jane Doe", "date_of_birth": "1990-05-15", "email": "jane@example.com"}'

# Create a consultation
curl -X POST http://localhost:8000/api/consultations/ \
  -H "Content-Type: application/json" \
  -d '{"patient": 1, "symptoms": "Persistent headache and dizziness", "diagnosis": "Migraine"}'

# Generate AI summary
curl -X POST http://localhost:8000/api/consultations/1/generate-summary/
```

---

## Running Tests

```bash
cd backend
source ../venv/bin/activate
python -m pytest -v
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | ✅ | — | Django secret key |
| `DEBUG` | ❌ | `True` | Debug mode |
| `ALLOWED_HOSTS` | ❌ | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `CORS_ALLOWED_ORIGINS` | ❌ | localhost variants | Comma-separated CORS origins |
| `OPENAI_API_KEY` | ❌ | — | OpenAI API key (mock used if unset) |
| `OPENAI_USE_MOCK` | ❌ | `false` | Force mock AI responses (`true`/`false`) |

---

## Tech Stack

- **Backend**: Django 6, Django REST Framework, Simple JWT, drf-yasg, python-dotenv
- **AI**: OpenAI Python SDK (gpt-3.5-turbo) with structured mock fallback
- **Frontend**: HTML5, Bootstrap 5, Vanilla JavaScript
- **Database**: SQLite (dev)
- **Tests**: pytest, pytest-django
- **Infrastructure**: Docker, docker-compose, nginx (frontend)
