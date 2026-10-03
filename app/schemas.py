import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, Field, field_validator

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    role: str = Field(..., description="doctor or patient")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ["doctor", "patient" ]:
            raise ValueError("Role must be one of: doctor, patient")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


# --- Doctor Schemas ---
class DoctorCreate(BaseModel):
    full_name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    qualification: str = Field(..., min_length=2)
    phone_number: str = Field(..., min_length=5)
    email: EmailStr
    consultation_fee: float = Field(..., gt=0)
    available_timings: str = Field(..., min_length=5, description="e.g. 'Mon-Fri 09:00 - 17:00'")

class DoctorUpdate(BaseModel):
    full_name: Optional[str] = None
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    consultation_fee: Optional[float] = None
    available_timings: Optional[str] = None

class DoctorResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    full_name: str
    specialization: str
    qualification: str
    phone_number: str
    email: str
    consultation_fee: float
    available_timings: str

    class Config:
        from_attributes = True


# --- Patient Schemas ---
class PatientCreate(BaseModel):
    full_name: str = Field(..., min_length=2)
    age: int = Field(..., gt=0, lt=150)
    gender: str = Field(...)
    phone_number: str = Field(..., min_length=5)
    address: str = Field(..., min_length=5)
    blood_group: str = Field(...)
    emergency_contact: str = Field(..., min_length=5)

class PatientUpdate(BaseModel):
    user_id: Optional[int] = None
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact: Optional[str] = None

class PatientResponse(BaseModel):
    id: int
    full_name: str
    age: int
    gender: str
    phone_number: str
    address: str
    blood_group: str
    emergency_contact: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Appointment Schemas ---
class AppointmentCreate(BaseModel):
    patient_id: Optional[int] = None
    doctor_id: int
    appointment_date: datetime.date
    time_slot: str = Field(..., description="e.g. '09:00 - 09:30'")
    reason_for_visit: str = Field(..., min_length=3)

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime.date] = None
    time_slot: Optional[str] = None
    reason_for_visit: Optional[str] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["Scheduled", "Confirmed", "Completed", "Cancelled", "No Show"]:
            raise ValueError("Status must be one of: Scheduled, Confirmed, Completed, Cancelled, No Show")
        return v

class AppointmentStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ["Scheduled", "Confirmed", "Completed", "Cancelled", "No Show"]:
            raise ValueError("Status must be one of: Scheduled, Confirmed, Completed, Cancelled, No Show")
        return v

class AppointmentResponse(BaseModel):
    id: int
    appointment_number: str
    patient_id: int
    doctor_id: int
    appointment_date: datetime.date
    time_slot: str
    reason_for_visit: str
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    patient: PatientResponse
    doctor: DoctorResponse

    class Config:
        from_attributes = True


# --- Prescription Schemas ---
class PrescriptionCreate(BaseModel):
    appointment_id: int
    diagnosis: str = Field(..., min_length=3)
    medicines: List[Any] = Field(..., description="List of medicines, e.g. details, name, strength, dosage")
    dosage: str = Field(...)
    instructions: str = Field(...)
    follow_up_date: Optional[datetime.date] = None

class PrescriptionUpdate(BaseModel):
    diagnosis: Optional[str] = None
    medicines: Optional[List[Any]] = None
    dosage: Optional[str] = None
    instructions: Optional[str] = None
    follow_up_date: Optional[datetime.date] = None

class PrescriptionResponse(BaseModel):
    id: int
    appointment_id: int
    doctor_id: int
    patient_id: int
    diagnosis: str
    medicines: List[Any]
    dosage: str
    instructions: str
    follow_up_date: Optional[datetime.date] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Medical Record Schemas ---
class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: int
    file_name: str
    file_path: str
    file_type: str
    uploaded_at: datetime.datetime

    class Config:
        from_attributes = True


# --- Audit Log Schemas ---
class AuditLogResponse(BaseModel):
    id: int
    appointment_id: int
    action: str
    changed_by: str
    previous_status: Optional[str] = None
    new_status: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True


# --- Report Schemas ---
class DashboardReport(BaseModel):
    total_patients: int
    total_doctors: int
    today_appointments: int
    upcoming_appointments: int
    completed_appointments: int
    cancelled_appointments: int
    most_visited_doctor: Optional[str] = None
    average_daily_appointments: float

class AppointmentsReport(BaseModel):
    total_appointments: int
    scheduled: int
    confirmed: int
    completed: int
    cancelled: int
    no_show: int

class DoctorReportItem(BaseModel):
    doctor_id: int
    doctor_name: str
    appointment_count: int

class DoctorsReport(BaseModel):
    doctors: List[DoctorReportItem]
