from pydantic import BaseModel, constr
from typing import Optional

# =========================
# USER SCHEMAS
# =========================

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=4, max_length=72)
    role: str


class UserLogin(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=4, max_length=72)


# =========================
# PATIENT SCHEMAS
# =========================

class PatientCreate(BaseModel):
    name: constr(min_length=2, max_length=100)
    phone: constr(min_length=7, max_length=20)
    age: int


# =========================
# APPOINTMENT SCHEMAS
# =========================

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    date: str


# =========================
# PRESCRIPTION SCHEMAS (FIXED)
# =========================

class PrescriptionCreate(BaseModel):
    patient_id: int
    doctor_id: int
    medicines: str
    notes: Optional[str] = None