import datetime

def test_appointment_booking_and_double_booking(client):
    # Register and login admin to create doctor
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

    # Register doctor profile
    doc_resp = client.post("/doctors", json={
        "full_name": "Dr. Sarah Connor",
        "specialization": "Pediatrics",
        "qualification": "MD",
        "phone_number": "1112223333",
        "email": "sarah@clinic.com",
        "consultation_fee": 1000.0,
        "available_timings": "Mon-Fri 09:00-12:00"
    }, headers=admin_headers)
    doctor_id = doc_resp.json()["id"]

    # Register and login receptionist to register patient and schedule appointment
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

    # Create patient
    pat_resp = client.post("/patients", json={
        "full_name": "John Connor",
        "age": 15,
        "gender": "Male",
        "phone_number": "2223334444",
        "address": "789 Broadway, Los Angeles",
        "blood_group": "AB-negative",
        "emergency_contact": "2223334445"
    }, headers=recep_headers)
    patient_id = pat_resp.json()["id"]

    # Book first appointment
    appt_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    appt_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_date": appt_date,
        "time_slot": "10:00 - 10:30",
        "reason_for_visit": "Regular Checkup"
    }
    book_resp = client.post("/appointments", json=appt_payload, headers=recep_headers)
    assert book_resp.status_code == 201
    appt_data = book_resp.json()
    assert appt_data["status"] == "Scheduled"
    assert appt_data["appointment_number"] is not None

    # Try to book SECOND appointment for same doctor and same time slot (Double Booking)
    double_book_payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_date": appt_date,
        "time_slot": "10:00 - 10:30",
        "reason_for_visit": "Second Opinion"
    }
    double_resp = client.post("/appointments", json=double_book_payload, headers=recep_headers)
    assert double_resp.status_code == 400
    assert "Double booking" in double_resp.json()["detail"]

    # Test CSV Export
    csv_resp = client.get("/appointments/export/csv", headers=recep_headers)
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    assert "Appointment Number" in csv_resp.text
