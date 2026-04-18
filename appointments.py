from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Appointment
from schemas import AppointmentCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def add_appointment(a: AppointmentCreate, db: Session = Depends(get_db)):
    appointment = Appointment(**a.dict())
    db.add(appointment)
    db.commit()
    return appointment

@router.get("/")
def get_appointments(db: Session = Depends(get_db)):
    return db.query(Appointment).all()