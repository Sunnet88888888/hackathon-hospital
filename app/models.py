import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50))  # admin, doctor, receptionist
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    doctor_profile: Mapped[Optional["Doctor"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Doctor(Base):
    __tablename__ = "doctors"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    specialization: Mapped[str] = mapped_column(String(255))
    qualification: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    consultation_fee: Mapped[float] = mapped_column(Float)
    available_timings: Mapped[str] = mapped_column(String(255))  # e.g. "Mon-Fri 09:00 - 17:00"

    user: Mapped[Optional["User"]] = relationship(back_populates="doctor_profile")
    appointments: Mapped[List["Appointment"]] = relationship(back_populates="doctor")
    prescriptions: Mapped[List["Prescription"]] = relationship(back_populates="doctor")

class Patient(Base):
    __tablename__ = "patients"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(50))
    phone_number: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(String(500))
    blood_group: Mapped[str] = mapped_column(String(20))
    emergency_contact: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    appointments: Mapped[List["Appointment"]] = relationship(back_populates="patient", cascade="all, delete")
    prescriptions: Mapped[List["Prescription"]] = relationship(back_populates="patient", cascade="all, delete")
    medical_records: Mapped[List["MedicalRecord"]] = relationship(back_populates="patient", cascade="all, delete")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_number: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"))
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"))
    appointment_date: Mapped[datetime.date] = mapped_column(Date)
    time_slot: Mapped[str] = mapped_column(String(100))
    reason_for_visit: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="Scheduled")  # Scheduled, Confirmed, Completed, Cancelled, No Show
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    patient: Mapped["Patient"] = relationship(back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship(back_populates="appointments")
    prescription: Mapped[Optional["Prescription"]] = relationship(back_populates="appointment")
    audit_logs: Mapped[List["AuditLog"]] = relationship(back_populates="appointment", cascade="all, delete")

class Prescription(Base):
    __tablename__ = "prescriptions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id", ondelete="CASCADE"))
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"))
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"))
    diagnosis: Mapped[str] = mapped_column(String(500))
    medicines: Mapped[list] = mapped_column(JSON)  # list of dicts/strings
    dosage: Mapped[str] = mapped_column(String(255))
    instructions: Mapped[str] = mapped_column(String(500))
    follow_up_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    appointment: Mapped["Appointment"] = relationship(back_populates="prescription")
    doctor: Mapped["Doctor"] = relationship(back_populates="prescriptions")
    patient: Mapped["Patient"] = relationship(back_populates="prescriptions")

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"))
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(50))  # pdf, jpg, png
    uploaded_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    patient: Mapped["Patient"] = relationship(back_populates="medical_records")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id", ondelete="CASCADE"))
    action: Mapped[str] = mapped_column(String(100))  # Booked, Rescheduled, Cancelled, Completed, Status Updated
    changed_by: Mapped[str] = mapped_column(String(255))  # user role + name
    previous_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50))
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    appointment: Mapped["Appointment"] = relationship(back_populates="audit_logs")
