from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Appointment
from schemas import AppointmentCreate

router = APIRouter()

# =========================
# DB SESSION
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# CREATE APPOINTMENT (FIXED)
# =========================
@router.post("/")
def add_appointment(a: AppointmentCreate, db: Session = Depends(get_db)):

    # 🔥 VALIDATION (VERY IMPORTANT)
    if not a.patient_id or not a.doctor_id:
        raise HTTPException(
            status_code=400,
            detail="patient_id and doctor_id are required"
        )

    appointment = Appointment(
        patient_id=int(a.patient_id),
        doctor_id=int(a.doctor_id),
        date=a.date
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment


# =========================
# GET ALL APPOINTMENTS
# =========================
@router.post("/")
def add_appointment(a: AppointmentCreate, db: Session = Depends(get_db)):

    appointment = Appointment(
        patient_id=int(a.patient_id),
        doctor_id=int(a.doctor_id),
        date=a.date
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment