from datetime import datetime
from typing import Optional

from pydantic import BaseModel, constr, EmailStr


# =========================
# USER SCHEMAS
# =========================

class UserCreate(BaseModel):

    clinic_name: constr(min_length=2, max_length=100)

    email: EmailStr

    username: constr(min_length=3, max_length=50)

    password: constr(min_length=4, max_length=72)

    role: str = "admin"


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

    date: datetime


# =========================
# PRESCRIPTION SCHEMAS
# =========================

class PrescriptionCreate(BaseModel):

    patient_id: int

    doctor_id: int

    medicines: str

    notes: Optional[str] = None


# =========================
# PAYMENT SCHEMAS
# =========================

class PaymentCreate(BaseModel):

    clinic_id: int

    amount: int

    currency: str = "USD"

    provider: str