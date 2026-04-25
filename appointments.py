from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Appointment
from schemas import AppointmentCreate

router = APIRouter()

# ================= DB =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= CREATE =================
@router.post("/")
def create_appointment(a: AppointmentCreate, db: Session = Depends(get_db)):

    if not a.patient_id or not a.doctor_id or not a.date:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields"
        )

    new_appointment = Appointment(
        patient_id=int(a.patient_id),
        doctor_id=int(a.doctor_id),
        date=a.date
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment

# ================= GET ALL =================
@router.get("/")
def get_appointments(db: Session = Depends(get_db)):
    return db.query(Appointment).all()