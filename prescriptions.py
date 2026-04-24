from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Prescription
from schemas import PrescriptionCreate

router = APIRouter()  # ❗ NO PREFIX HERE

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        from fastapi import APIRouter, Depends
        from sqlalchemy.orm import Session
        from database import SessionLocal
        from models import Prescription

        router = APIRouter(prefix="/api/prescriptions", tags=["Prescriptions"])

        # DB
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()

        # =========================
        # GET ALL PRESCRIPTIONS (MISSING PART)
        # =========================
        @router.get("/")
        def get_prescriptions(db: Session = Depends(get_db)):
            return db.query(Prescription).all()

        # =========================
        # CREATE PRESCRIPTION
        # =========================
        @router.post("/")
        def create_prescription(p: PrescriptionCreate, db: Session = Depends(get_db)):
            new_prescription = Prescription(
                patient_id=p.patient_id,
                doctor_id=p.doctor_id,
                medicines=p.medicines,
                notes=p.notes
            )

            db.add(new_prescription)
            db.commit()
            db.refresh(new_prescription)

            return new_prescription

@router.post("/")
def create_prescription(p: PrescriptionCreate, db: Session = Depends(get_db)):
    new_prescription = Prescription(
        patient_id=p.patient_id,
        doctor_id=p.doctor_id,
        medicines=p.medicines,
        notes=p.notes
    )

    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)

    return new_prescription