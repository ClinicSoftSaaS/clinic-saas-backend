from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import SessionLocal

from models import Patient, Appointment, Prescription
from schemas import PatientCreate
from security import get_current_user

from subscription_guard import check_subscription

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
def add_patient(
    p: PatientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    clinic_id = current_user["clinic_id"]

    # 🔐 SUBSCRIPTION CHECK
    check_subscription(db, clinic_id)

    try:
        patient = Patient(
            name=p.name,
            phone=p.phone,
            age=p.age,
            clinic_id=clinic_id
        )

        db.add(patient)
        db.commit()
        db.refresh(patient)

        return patient

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Patient with this phone already exists"
        )

    except Exception as e:
        db.rollback()
        print("ADD PATIENT ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )


# =========================
# GET ALL PATIENTS
# =========================
@router.get("/")
def get_patients(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    clinic_id = current_user["clinic_id"]

    check_subscription(db, clinic_id)

    patients = db.query(Patient).filter(
        Patient.clinic_id == clinic_id
    ).all()

    return patients


# =========================
# SEARCH BY PHONE
# =========================
@router.get("/search/phone/{phone}")
def search_by_phone(
    phone: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    clinic_id = current_user["clinic_id"]

    check_subscription(db, clinic_id)

    patient = db.query(Patient).filter(
        Patient.phone == phone,
        Patient.clinic_id == clinic_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


# =========================
# SEARCH BY ID
# =========================
@router.get("/search/id/{id}")
def search_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    clinic_id = current_user["clinic_id"]

    check_subscription(db, clinic_id)

    patient = db.query(Patient).filter(
        Patient.id == id,
        Patient.clinic_id == clinic_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


# =========================
# PATIENT HISTORY
# =========================
@router.get("/history/{patient_id}")
def patient_history(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    clinic_id = current_user["clinic_id"]

    check_subscription(db, clinic_id)

    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.clinic_id == clinic_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id,
        Appointment.clinic_id == clinic_id
    ).all()

    prescriptions = db.query(Prescription).filter(
        Prescription.patient_id == patient_id,
        Prescription.clinic_id == clinic_id
    ).all()

    return {
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "phone": patient.phone,
            "age": patient.age
        },
        "appointments": [
            {
                "id": a.id,
                "date": a.date,
                "doctor_id": a.doctor_id
            } for a in appointments
        ],
        "prescriptions": [
            {
                "id": p.id,
                "medicines": p.medicines,
                "notes": p.notes,
                "date": p.date
            } for p in prescriptions
        ]
    }