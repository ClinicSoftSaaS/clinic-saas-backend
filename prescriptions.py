from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Prescription
from pydantic import BaseModel
from datetime import datetime

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
# SCHEMA (IMPORTANT FIX)
# =========================
class PrescriptionCreate(BaseModel):
    patient_id: int
    doctor_id: int
    medicines: str
    notes: str


# =========================
# CREATE PRESCRIPTION
# =========================
@router.post("/")
def add_prescription(data: PrescriptionCreate, db: Session = Depends(get_db)):
    try:
        new_p = Prescription(
            patient_id=data.patient_id,
            doctor_id=data.doctor_id,
            medicines=data.medicines,
            notes=data.notes,
            date=datetime.utcnow()
        )

        db.add(new_p)
        db.commit()
        db.refresh(new_p)

        return {
            "message": "Prescription saved",
            "id": new_p.id
        }

    except Exception as e:
        print("Prescription Error:", e)
        raise HTTPException(status_code=500, detail="Failed to save prescription")


# =========================
# GET PRESCRIPTIONS
# =========================
@router.get("/{patient_id}")
def get_prescriptions(patient_id: int, db: Session = Depends(get_db)):
    return db.query(Prescription).filter(
        Prescription.patient_id == patient_id
    ).all()