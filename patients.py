from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Patient
from schemas import PatientCreate

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def add_patient(p: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**p.dict())
    db.add(patient)
    db.commit()
    return patient

@router.get("/")
def get_patients(db: Session = Depends(get_db)):
    return db.query(Patient).all()
@router.get("/search/phone/{phone}")
def search_by_phone(phone: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.phone == phone).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient


@router.get("/search/id/{id}")
def search_by_id(id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient