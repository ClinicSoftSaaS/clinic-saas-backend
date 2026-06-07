from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Appointment, Patient, User
from schemas import AppointmentCreate
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


# ================= CREATE APPOINTMENT =================
@router.post("/")
def create_appointment(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    clinic_id = current_user["clinic_id"]

    # 🔐 SUBSCRIPTION CHECK
    check_subscription(db, clinic_id)

    # ================= VALIDATE PATIENT =================
    patient = db.query(Patient).filter(
        Patient.id == data.patient_id,
        Patient.clinic_id == clinic_id
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found in your clinic"
        )

    # ================= VALIDATE DOCTOR =================
    doctor = db.query(User).filter(
        User.id == data.doctor_id,
        User.clinic_id == clinic_id
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found in your clinic"
        )

    # ================= CREATE APPOINTMENT =================
    try:
        appointment = Appointment(
            patient_id=data.patient_id,
            doctor_id=data.doctor_id,
            date=data.date,
            clinic_id=clinic_id
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        return {
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "doctor_id": appointment.doctor_id,
            "date": appointment.date,
            "message": "Appointment created successfully"
        }

    except Exception as e:
        db.rollback()
        print("APPOINTMENT ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )


# ================= GET ALL APPOINTMENTS =================
@router.get("/")
def get_appointments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    clinic_id = current_user["clinic_id"]

    # 🔐 SUBSCRIPTION CHECK
    check_subscription(db, clinic_id)

    appointments = db.query(Appointment).filter(
        Appointment.clinic_id == clinic_id
    ).all()

    # ================= CLEAN RESPONSE =================
    return [
        {
            "id": a.id,
            "patient_id": a.patient_id,
            "doctor_id": a.doctor_id,
            "date": a.date
        }
        for a in appointments
    ]