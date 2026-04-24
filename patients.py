from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Patient, Appointment, Prescription
from schemas import PatientCreate

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
# CREATE PATIENT
# =========================
@router.post("/")
def add_patient(p: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**p.dict())

    try:
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Phone number already exists"
        )


# =========================
# GET ALL PATIENTS
# =========================
@router.get("/")
def get_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()


# =========================
# SEARCH BY PHONE
# =========================
@router.get("/search/phone/{phone}")
def search_by_phone(phone: str, db: Session = Depends(get_db)):

    patient = db.query(Patient).filter(Patient.phone == phone).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient


# =========================
# SEARCH BY ID
# =========================
@router.get("/search/id/{id}")
def search_by_id(id: int, db: Session = Depends(get_db)):

    patient = db.query(Patient).filter(Patient.id == id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient


# =========================
# PATIENT FULL HISTORY
# =========================
@router.get("/history/{patient_id}")
def patient_history(patient_id: int, db: Session = Depends(get_db)):

    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).all()

    prescriptions = db.query(Prescription).filter(
        Prescription.patient_id == patient_id
    ).all()

    return {
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "phone": patient.phone,
            "age": patient.age
        },
        "appointments": appointments,
        "prescriptions": prescriptions
    }