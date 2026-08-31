def test_register_user(client):
    payload = {
        "email": "admin@clinic.com",
        "password": "adminpassword123",
        "full_name": "Clinic Admin",
        "role": "admin"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "admin@clinic.com"
    assert data["role"] == "admin"
    assert "id" in data

def test_register_existing_user(client):
    payload = {
        "email": "admin@clinic.com",
        "password": "adminpassword123",
        "full_name": "Clinic Admin",
        "role": "admin"
    }
    # Register once
    client.post("/auth/register", json=payload)
    # Register twice
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client):
    # Register user
    client.post("/auth/register", json={
        "email": "admin@clinic.com",
        "password": "adminpassword123",
        "full_name": "Clinic Admin",
        "role": "admin"
    })
    
    # Login
    response = client.post("/auth/login", json={
        "email": "admin@clinic.com",
        "password": "adminpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_credentials(client):
    response = client.post("/auth/login", json={
        "email": "nonexistent@clinic.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "detail" in response.json()
