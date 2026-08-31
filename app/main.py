from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.config import settings
from app.database import engine, Base
from app.routes import auth, doctors, patients, appointments, prescriptions, records, reports

# Automatically create tables for quick execution if needed
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Clinic Management System",
    description="Backend platform enabling clinics to manage users, doctors, patients, appointments, prescriptions, and medical records.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount upload directory as static files (useful for downloading or viewing uploaded reports)
app.mount(f"/{settings.UPLOAD_DIR}", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(prescriptions.router)
app.include_router(records.router)
app.include_router(reports.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to the Clinic Management System API",
        "docs": "/docs"
    }
