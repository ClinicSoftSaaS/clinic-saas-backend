from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Appointment
from schemas import AppointmentCreate

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])

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
# CREATE APPOINTMENT
# =========================
@router.post("/")
def add_appointment(a: AppointmentCreate, db: Session = Depends(get_db)):

    if not a.patient_id or not a.doctor_id or not a.date:
        raise HTTPException(
            status_code=400,
            detail="patient_id, doctor_id and date are required"
        )

    appointment = Appointment(
        patient_id=int(a.patient_id),   # 🔥 FORCE INTEGER
        doctor_id=int(a.doctor_id),     # 🔥 FORCE INTEGER
        date=a.date
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment

# =========================
# GET ALL APPOINTMENTS (FIXED)
# =========================
@router.get("/")
def get_appointments(db: Session = Depends(get_db)):
    appointments = db.query(Appointment).all()

    return [
        {
            "id": a.id,
            "patient_id": a.patient_id,
            "doctor_id": a.doctor_id,
            "date": a.date
        }
        for a in appointments
    ]