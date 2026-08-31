def test_patient_crud(client):
    # Register and login receptionist
    client.post("/auth/register", json={
        "email": "receptionist@clinic.com",
        "password": "receppassword123",
        "full_name": "Clinic Receptionist",
        "role": "receptionist"
    })
    login_resp = client.post("/auth/login", json={
        "email": "receptionist@clinic.com",
        "password": "receppassword123"
    })
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Register Patient
    patient_payload = {
        "full_name": "Jane Smith",
        "age": 32,
        "gender": "Female",
        "phone_number": "9876543210",
        "address": "456 Main St, New York",
        "blood_group": "O-positive",
        "emergency_contact": "9876543211"
    }
    create_resp = client.post("/patients", json=patient_payload, headers=headers)
    assert create_resp.status_code == 201
    p_data = create_resp.json()
    assert p_data["full_name"] == "Jane Smith"
    
    # Get Patient details
    p_id = p_data["id"]
    get_resp = client.get(f"/patients/{p_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["blood_group"] == "O-positive"

    # Update Patient details
    update_payload = {"age": 33}
    update_resp = client.put(f"/patients/{p_id}", json=update_payload, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["age"] == 33
