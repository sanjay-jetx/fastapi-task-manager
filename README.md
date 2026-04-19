# FastAPI Task Manager

A full-stack Task Manager web application with a **FastAPI** backend and a **Vanilla JS + HTML/CSS** frontend. Built as part of a Python Developer Intern assignment.

## Project Overview

- ✅ User Registration & Login with **JWT Authentication**
- ✅ Full Task CRUD: Create, View All, View by ID, Mark Complete, Delete
- ✅ Tasks are **user-scoped** — users can only access their own tasks
- ✅ **Pagination** (`?skip=0&limit=10`) and **filtering** (`?completed=true`) on task listing
- ✅ Static frontend served directly by FastAPI (`/frontend`)
- ✅ Swagger API docs available at `/docs`

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | FastAPI, SQLAlchemy, SQLite        |
| Auth       | JWT (`python-jose`), bcrypt        |
| Validation | Pydantic v2                       |
| Frontend   | HTML5, CSS3, Vanilla JavaScript   |
| Tests      | pytest, httpx, FastAPI TestClient |
| Deployment | Docker, Render / Railway          |

## Folder Structure

```
fastapi-task-manager/
├── app/
│   ├── core/           # Security (JWT, hashing)
│   ├── dependencies/   # Auth dependency (get_current_user)
│   ├── models/         # SQLAlchemy models
│   ├── routes/         # API route handlers
│   ├── schemas/        # Pydantic request/response schemas
│   ├── database.py     # DB engine, session, get_db
│   └── main.py         # App entry point
├── frontend/           # Static HTML/CSS/JS frontend
├── tests/              # pytest test suite
├── .env.example        # Environment variable template
├── Dockerfile          # Container build definition
├── pytest.ini          # Pytest config
└── requirements.txt
```

## API Endpoints

| Method | Endpoint        | Auth | Description          |
|--------|-----------------|------|----------------------|
| POST   | `/register`     | ❌   | Register a new user  |
| POST   | `/login`        | ❌   | Login, get JWT token |
| POST   | `/tasks`        | ✅   | Create a task        |
| GET    | `/tasks`        | ✅   | List tasks (paginated, filterable) |
| GET    | `/tasks/{id}`   | ✅   | Get a specific task  |
| PUT    | `/tasks/{id}`   | ✅   | Update / complete a task |
| DELETE | `/tasks/{id}`   | ✅   | Delete a task        |

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd fastapi-task-manager
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Variables

Copy the template and fill in values:
```bash
cp .env.example .env
```

| Variable       | Description                              | Example                    |
|----------------|------------------------------------------|----------------------------|
| `SECRET_KEY`   | Random secret for JWT signing            | `openssl rand -hex 32`     |
| `DATABASE_URL` | SQLAlchemy database URL                  | `sqlite:///./test.db`      |

### 4. Run Locally
```bash
uvicorn app.main:app --reload
```
- **App:** [http://localhost:8000/](http://localhost:8000/)
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Run Tests
```bash
pytest
```

### 6. Run with Docker
```bash
docker build -t fastapi-task-manager .
docker run -p 8000:8000 --env-file .env fastapi-task-manager
```

## Deployment

Deployed on **Render / Railway**: [Insert your live URL here]

> Set `SECRET_KEY` and `DATABASE_URL` as environment variables in your hosting dashboard. Do **not** commit `.env`.
