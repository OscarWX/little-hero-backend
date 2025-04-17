from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Little Hero Backend API"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_heroes():
    response = client.get("/heroes")
    assert response.status_code == 200
    assert len(response.json()) == 3  # Check that we have our 3 initial heroes

def test_get_hero():
    response = client.get("/heroes/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Super Swift"

def test_hero_not_found():
    response = client.get("/heroes/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Hero not found"}

def test_create_hero():
    hero_data = {
        "name": "Aqua Master",
        "power": "Water Control",
        "description": "Can manipulate water in all forms"
    }
    response = client.post("/heroes", json=hero_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Aqua Master"
    assert response.json()["id"] is not None  # Ensure an ID was assigned 