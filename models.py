from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from database import Base
import datetime


# =========================
# CLINIC TABLE
# =========================
class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    plan = Column(String, default="trial")
    max_users = Column(Integer, default=1)

    subscription_status = Column(String, default="trialing")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# =========================
# USER TABLE (UPDATED FOR TRIAL SYSTEM)
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), index=True, nullable=False)

    name = Column(String)
    email = Column(String, unique=True)
    whatsapp = Column(String)

    username = Column(String, unique=True, index=True)
    password = Column(String)

    role = Column(String)  # admin / doctor / patient

    trial_start = Column(DateTime, default=datetime.datetime.utcnow)
    trial_end = Column(DateTime)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# =========================
# PATIENT TABLE
# =========================
# =========================
# PATIENT TABLE
# =========================
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), index=True, nullable=False)

    name = Column(String)
    phone = Column(String, index=True)
    age = Column(Integer)

    # NEW FIELDS
    gender = Column(String)
    address = Column(String)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# =========================
# APPOINTMENT TABLE
# =========================
class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), index=True, nullable=False)

    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))

    date = Column(DateTime, default=datetime.datetime.utcnow)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# =========================
# PRESCRIPTION TABLE
# =========================
class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), index=True, nullable=False)

    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("users.id"))

    medicines = Column(Text)
    notes = Column(Text)

    date = Column(DateTime, default=datetime.datetime.utcnow)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# =========================
# CLINIC PLAN TABLE
# =========================
class ClinicPlan(Base):
    __tablename__ = "clinic_plans"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), unique=True, index=True)

    plan_name = Column(String)
    max_users = Column(Integer)
    monthly_price = Column(Integer, default=0)

    is_active = Column(String, default="active")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# =========================
# PAYMENT TABLE (LOW LEVEL)
# =========================
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), index=True, nullable=False)

    amount = Column(Integer)
    currency = Column(String, default="PKR")

    provider = Column(String)

    status = Column(String, default="pending")

    transaction_id = Column(String, nullable=True)
    proof_url = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# =========================
# PAYMENT PROOF TABLE (ADMIN SYSTEM)
# =========================
class PaymentProof(Base):
    __tablename__ = "payment_proofs"

    id = Column(Integer, primary_key=True, index=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id"), index=True, nullable=False)

    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)

    plan = Column(String)
    amount = Column(Integer)

    screenshot_url = Column(String, nullable=True)

    status = Column(String, default="pending")

    proof_method = Column(String, default="whatsapp")

    admin_note = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# =========================
# PAYMENT REQUEST (CLEAN SYSTEM - MAIN ONE)
# =========================
class PaymentRequest(Base):
    __tablename__ = "payment_requests"

    id = Column(Integer, primary_key=True, index=True)

    clinic_id = Column(Integer, ForeignKey("clinics.id"), index=True, nullable=False)

    plan = Column(String)
    amount = Column(Integer)

    status = Column(String, default="pending")  # pending / approved / rejected

    proof_method = Column(String, default="whatsapp")

    admin_note = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)