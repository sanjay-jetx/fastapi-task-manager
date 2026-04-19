import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Use a separate test database file
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_in_memory.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def unique_email():
    """Generate a unique email for each test run to avoid DB state conflicts."""
    return f"user_{uuid.uuid4().hex[:8]}@example.com"

# --- Helper to get a fresh token ---
def get_token():
    email = "tasktest@example.com"
    password = "securepass123"
    client.post("/register", json={"email": email, "password": password})
    res = client.post("/login", json={"email": email, "password": password})
    return res.json()["access_token"]

# ─── Auth Tests ───────────────────────────────────────────────

def test_register_new_user():
    email = unique_email()
    response = client.post("/register", json={"email": email, "password": "password123"})
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully"

def test_register_duplicate_user():
    client.post("/register", json={"email": "dupe@example.com", "password": "password123"})
    response = client.post("/register", json={"email": "dupe@example.com", "password": "password123"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_login_success():
    client.post("/register", json={"email": "logintest@example.com", "password": "password123"})
    response = client.post("/login", json={"email": "logintest@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password():
    client.post("/register", json={"email": "wrongpass@example.com", "password": "correctpass"})
    response = client.post("/login", json={"email": "wrongpass@example.com", "password": "wrongpass"})
    assert response.status_code == 401

# ─── Task Tests ───────────────────────────────────────────────

def test_create_task():
    token = get_token()
    response = client.post(
        "/tasks",
        json={"title": "My test task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My test task"
    assert data["completed"] == False

def test_get_all_tasks():
    token = get_token()
    response = client.get("/tasks", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_all_tasks_filter_completed():
    token = get_token()
    response = client.get("/tasks?completed=false", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    tasks = response.json()
    assert all(t["completed"] == False for t in tasks)

def test_get_task_by_id():
    token = get_token()
    # Create task first
    created = client.post("/tasks", json={"title": "Get by ID task"}, headers={"Authorization": f"Bearer {token}"})
    task_id = created.json()["id"]
    # Fetch it
    response = client.get(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == task_id

def test_get_task_not_found():
    token = get_token()
    response = client.get("/tasks/99999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_update_task_mark_completed():
    token = get_token()
    created = client.post("/tasks", json={"title": "Task to complete"}, headers={"Authorization": f"Bearer {token}"})
    task_id = created.json()["id"]
    response = client.put(
        f"/tasks/{task_id}",
        json={"completed": True},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["completed"] == True

def test_delete_task():
    token = get_token()
    created = client.post("/tasks", json={"title": "Task to delete"}, headers={"Authorization": f"Bearer {token}"})
    task_id = created.json()["id"]
    response = client.delete(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204
    # Verify it's gone
    verify = client.get(f"/tasks/{task_id}", headers={"Authorization": f"Bearer {token}"})
    assert verify.status_code == 404

def test_access_task_without_token():
    response = client.get("/tasks")
    assert response.status_code == 401
