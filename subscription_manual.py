from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import SessionLocal
from models import Clinic, PaymentProof

router = APIRouter()

# =========================
# PLAN CONFIGURATION
# =========================
PLAN_CONFIG = {
    "trial": 1,
    "basic": 2,
    "pro": 5
}

PLAN_PRICE = {
    "basic": 2000,
    "pro": 3500
}

WHATSAPP_NUMBER = "+923226813940"
JAZZCASH_NUMBER = "+923226813940"

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
# GET PLANS
# =========================
@router.get("/plans")
def get_plans():
    return [
        {"name": "basic", "price": 2000, "max_users": 2},
        {"name": "pro", "price": 3500, "max_users": 5}
    ]

# =========================
# SELECT PLAN (CREATE PAYMENT REQUEST)
# =========================
@router.post("/select-plan")
def select_plan(data: dict, db: Session = Depends(get_db)):

    clinic_id = data.get("clinic_id")
    plan = data.get("plan")

    if not clinic_id:
        raise HTTPException(status_code=400, detail="clinic_id is required")

    if plan not in PLAN_PRICE:
        raise HTTPException(status_code=400, detail="Invalid plan")

    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()

    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    amount = PLAN_PRICE[plan]

    payment = PaymentProof(
        clinic_id=clinic_id,
        plan=plan,
        amount=amount,
        screenshot_url="pending_whatsapp",
        status="pending",
        created_at=datetime.utcnow()
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Plan selected successfully",
        "clinic_id": clinic_id,
        "plan": plan,
        "amount": amount,
        "whatsapp": WHATSAPP_NUMBER,
        "jazzcash": JAZZCASH_NUMBER,
        "payment_id": payment.id,
        "status": "pending"
    }

# =========================
# CLINIC STATUS
# =========================
@router.get("/clinic/{clinic_id}")
def get_clinic_plan(clinic_id: int, db: Session = Depends(get_db)):

    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()

    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    return {
        "clinic_id": clinic.id,
        "clinic_name": clinic.name,
        "plan": clinic.plan,
        "max_users": clinic.max_users,
        "subscription_status": clinic.subscription_status
    }

# =========================
# ADMIN: VIEW PAYMENTS
# =========================
@router.get("/admin/payment-proofs")
def get_payment_proofs(db: Session = Depends(get_db)):

    proofs = db.query(PaymentProof).order_by(PaymentProof.id.desc()).all()

    return proofs

# =========================
# ADMIN: APPROVE PAYMENT
# =========================
@router.post("/admin/approve-payment/{proof_id}")
def approve_payment(proof_id: int, db: Session = Depends(get_db)):

    proof = db.query(PaymentProof).filter(PaymentProof.id == proof_id).first()

    if not proof:
        raise HTTPException(status_code=404, detail="Payment not found")

    clinic = db.query(Clinic).filter(Clinic.id == proof.clinic_id).first()

    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    # ACTIVATE SUBSCRIPTION
    clinic.plan = proof.plan
    clinic.max_users = PLAN_CONFIG.get(proof.plan, 1)
    clinic.subscription_status = "active"

    proof.status = "approved"

    db.commit()

    return {
        "message": "Payment approved",
        "clinic_id": clinic.id,
        "plan": clinic.plan,
        "status": "active"
    }

# =========================
# ADMIN: REJECT PAYMENT (FIXED)
# =========================
@router.post("/admin/reject-payment/{proof_id}")
def reject_payment(proof_id: int, db: Session = Depends(get_db)):

    proof = db.query(PaymentProof).filter(PaymentProof.id == proof_id).first()

    if not proof:
        raise HTTPException(status_code=404, detail="Payment not found")

    clinic = db.query(Clinic).filter(Clinic.id == proof.clinic_id).first()

    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    # ❌ BLOCK USER ACCESS PROPERLY
    proof.status = "rejected"
    clinic.subscription_status = "blocked"
    clinic.plan = "trial"
    clinic.max_users = 1

    db.commit()

    return {
        "message": "Payment rejected and user blocked",
        "status": "blocked"
    }

# =========================
# PAYMENT INFO
# =========================
@router.get("/payment-info")
def payment_info():
    return {
        "whatsapp": WHATSAPP_NUMBER,
        "jazzcash": JAZZCASH_NUMBER,
        "account_name": "Shahnaz Akhtar",
        "message": "Send payment screenshot on WhatsApp for activation"
    }