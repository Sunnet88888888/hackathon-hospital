def test_create_and_get_doctor(client):
    # Register and login admin
    client.post("/auth/register", json={
        "email": "admin@clinic.com",
        "password": "adminpassword123",
        "full_name": "Clinic Admin",
        "role": "admin"
    })
    login_resp = client.post("/auth/login", json={
        "email": "admin@clinic.com",
        "password": "adminpassword123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create doctor
    doc_payload = {
        "full_name": "Dr. John Doe",
        "specialization": "Cardiology",
        "qualification": "MD - Cardiology",
        "phone_number": "1234567890",
        "email": "johndoe@clinic.com",
        "consultation_fee": 1500.0,
        "available_timings": "Mon-Fri 09:00 - 13:00"
    }
    create_resp = client.post("/doctors", json=doc_payload, headers=headers)
    assert create_resp.status_code == 201
    doc_data = create_resp.json()
    assert doc_data["full_name"] == "Dr. John Doe"
    assert doc_data["specialization"] == "Cardiology"

    # Get list of doctors
    list_resp = client.get("/doctors")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # Get doctor by ID
    doc_id = doc_data["id"]
    get_resp = client.get(f"/doctors/{doc_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["email"] == "johndoe@clinic.com"

def test_create_doctor_unauthorized(client):
    # Attempt to create doctor without token
    doc_payload = {
        "full_name": "Dr. Unauthorized",
        "specialization": "Pediatrics",
        "qualification": "MBBS",
        "phone_number": "9999999999",
        "email": "unauthorized@clinic.com",
        "consultation_fee": 500.0,
        "available_timings": "Mon-Fri 14:00 - 18:00"
    }
    response = client.post("/doctors", json=doc_payload)
    assert response.status_code == 401
