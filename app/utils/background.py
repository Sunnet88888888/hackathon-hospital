import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BackgroundTasks")

def send_appointment_confirmation_email(patient_email: str, patient_name: str, appointment_number: str, appointment_date: str, time_slot: str, doctor_name: str):
    message = (
        f"\n==================================================\n"
        f"EMAIL SENT TO: {patient_email}\n"
        f"SUBJECT: Appointment Confirmation - {appointment_number}\n"
        f"Dear {patient_name},\n"
        f"Your appointment with Dr. {doctor_name} has been successfully scheduled.\n"
        f"Details:\n"
        f"  Appointment Number: {appointment_number}\n"
        f"  Date: {appointment_date}\n"
        f"  Time Slot: {time_slot}\n"
        f"Thank you for choosing our clinic!\n"
        f"=================================================="
    )
    logger.info(message)

def send_appointment_reminder_email(patient_email: str, patient_name: str, appointment_number: str, appointment_date: str, time_slot: str, doctor_name: str):
    message = (
        f"\n==================================================\n"
        f"EMAIL SENT TO: {patient_email}\n"
        f"SUBJECT: Appointment Reminder - {appointment_number}\n"
        f"Dear {patient_name},\n"
        f"This is a reminder for your upcoming appointment with Dr. {doctor_name}.\n"
        f"Details:\n"
        f"  Appointment Number: {appointment_number}\n"
        f"  Date: {appointment_date}\n"
        f"  Time Slot: {time_slot}\n"
        f"We look forward to seeing you.\n"
        f"=================================================="
    )
    logger.info(message)

def notify_patient_prescription_created(patient_email: str, patient_name: str, diagnosis: str, doctor_name: str):
    message = (
        f"\n==================================================\n"
        f"EMAIL SENT TO: {patient_email}\n"
        f"SUBJECT: New Prescription Issued\n"
        f"Dear {patient_name},\n"
        f"Dr. {doctor_name} has issued a new prescription for you.\n"
        f"Diagnosis: {diagnosis}\n"
        f"Please log in to your patient portal or contact reception to view complete prescription details.\n"
        f"=================================================="
    )
    logger.info(message)
