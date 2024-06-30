import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import SessionLocal
from app import models, database

SQLALCHEMY_DATABASE_URL = "postgresql://taskuser:taskpassword@localhost/taskdb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

database.Base.metadata.create_all(bind=engine)

def test_get_db():
    db_gen = get_db()
    db = next(db_gen)
    assert isinstance(db, SessionLocal().__class__)
    db_gen.close()

# Override the get_db dependency to use the testing database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_api_status():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "running"}


def test_create_task():
    response = client.post("/tasks/", json={"title": "Test Task", "description": "Test Description"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"
    assert response.json()["description"] == "Test Description"


def test_create_task_invalid():
    response = client.post("/tasks/", json={})
    assert response.status_code == 422 


def test_get_tasks():
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_task():
    response = client.post("/tasks/", json={"title": "Another Task", "description": "Another Description"})
    task_id = response.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_get_task_not_found():
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_update_task():
    response = client.post("/tasks/", json={"title": "Update Task", "description": "To be updated"})
    task_id = response.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={"title": "Updated Task", "description": "Updated description", "completed": True})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"
    assert response.json()["description"] == "Updated description"
    assert response.json()["completed"] is True


def test_update_task_not_found():
    response = client.put("/tasks/999", json={"title": "Updated Task", "description": "Updated description", "completed": True})
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_delete_task():
    response = client.post("/tasks/", json={"title": "Delete Task", "description": "To be deleted"})
    task_id = response.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_delete_task_not_found():
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}