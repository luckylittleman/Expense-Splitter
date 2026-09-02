from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_read_root():
    response=client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message":"Hello"}

def test_register_user():
    response = client.post("/users", json={"user_name":"TestUser","password":"testpass123"})
    assert response.status_code == 200
    data = response.json()
    assert data["user_name"] == "TestUser"
    assert "password_hash" not in data

def test_login_success():
    #register a user first
    client.post("/users", json={"user_name":"LoginTestUser","password":"correctpass"})
    response = client.post("/login", json={"user_name":"LoginTestUser","password":"correctpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_passwrord():
    response = client.post("/login", json={"user_name":"LoginTestUser", "password":"wrongpass"})
    assert response.status_code == 401

def test_delete_user_requirew_auth():
    response = client.delete("/users/1")
    assert response.status_code == 401