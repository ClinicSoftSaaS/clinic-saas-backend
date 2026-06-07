from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Prescription, Patient, User
from schemas import PrescriptionCreate
from security import get_current_user

from subscription_guard import check_subscription

router = APIRouter()


# ================= DB =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= GET ALL PRESCRIPTIONS =================
@router.get("/")
def get_prescriptions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    clinic_id = current_user["clinic_id"]

    # 🔐 SUBSCRIPTION CHECK
    check_subscription(db, clinic_id)

    prescriptions = db.query(Prescription).filter(
        Prescription.clinic_id == clinic_id
    ).all()

    # ================= CLEAN RESPONSE =================
    return [
        {
            "id": p.id,
            "patient_id": p.patient_id,
            "doctor_id": p.doctor_id,
            "medicines": p.medicines,
            "notes": p.notes,
            "date": p.date
        }
        for p in prescriptions
    ]


# ================= CREATE PRESCRIPTION =================
@router.post("/")
def create_prescription(
    p: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    clinic_id = current_user["clinic_id"]

    # 🔐 SUBSCRIPTION CHECK
    check_subscription(db, clinic_id)

    # ================= VERIFY PATIENT =================
    patient = db.query(Patient).filter(
        Patient.id == p.patient_id,
        Patient.clinic_id == clinic_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found in your clinic"
        )

    # ================= VERIFY DOCTOR =================
    doctor = db.query(User).filter(
        User.id == p.doctor_id,
        User.clinic_id == clinic_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found in your clinic"
        )

    # ================= CREATE PRESCRIPTION =================
    try:
        new_prescription = Prescription(
            patient_id=p.patient_id,
            doctor_id=p.doctor_id,
            medicines=p.medicines,
            notes=p.notes,
            clinic_id=clinic_id
        )

        db.add(new_prescription)
        db.commit()
        db.refresh(new_prescription)

        return {
            "id": new_prescription.id,
            "patient_id": new_prescription.patient_id,
            "doctor_id": new_prescription.doctor_id,
            "medicines": new_prescription.medicines,
            "notes": new_prescription.notes,
            "message": "Prescription created successfully"
        }

    except Exception as e:
        db.rollback()
        print("PRESCRIPTION ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )