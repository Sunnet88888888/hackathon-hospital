def test_reports_dashboard_access_and_metrics(client):
    # Register and login admin
    client.post("/auth/register", json={
        "email": "admin@clinic.com",
        "password": "adminpassword123",
        "full_name": "Clinic Admin",
        "role": "admin"
    })
    admin_login = client.post("/auth/login", json={
        "email": "admin@clinic.com",
        "password": "adminpassword123"
    })
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Register and login receptionist
    client.post("/auth/register", json={
        "email": "receptionist@clinic.com",
        "password": "receppassword123",
        "full_name": "Clinic Receptionist",
        "role": "receptionist"
    })
    recep_login = client.post("/auth/login", json={
        "email": "receptionist@clinic.com",
        "password": "receppassword123"
    })
    recep_token = recep_login.json()["access_token"]
    recep_headers = {"Authorization": f"Bearer {recep_token}"}

    # Try to access reports dashboard as receptionist (expecting 403 Forbidden)
    resp_receptionist = client.get("/reports/dashboard", headers=recep_headers)
    assert resp_receptionist.status_code == 403

    # Access reports dashboard as admin (expecting 200 Success)
    resp_admin = client.get("/reports/dashboard", headers=admin_headers)
    assert resp_admin.status_code == 200
    metrics = resp_admin.json()
    assert "total_patients" in metrics
    assert "total_doctors" in metrics
    assert "today_appointments" in metrics
    assert "upcoming_appointments" in metrics
    assert "completed_appointments" in metrics
    assert "cancelled_appointments" in metrics
    assert "average_daily_appointments" in metrics

    # Access appointments summary report
    resp_appts = client.get("/reports/appointments", headers=admin_headers)
    assert resp_appts.status_code == 200
    assert "total_appointments" in resp_appts.json()

    # Access doctors performance report
    resp_docs = client.get("/reports/doctors", headers=admin_headers)
    assert resp_docs.status_code == 200
    assert "doctors" in resp_docs.json()
