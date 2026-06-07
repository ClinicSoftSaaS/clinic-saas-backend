from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Clinic, Payment  # ✅ FIXED (NO PaymentRequest)

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
# USER SUBMIT PAYMENT PROOF (OPTIONAL FLOW)
# =========================
@router.post("/submit-payment")
def submit_payment(data: dict, db: Session = Depends(get_db)):

    clinic_id = data.get("clinic_id")
    amount = data.get("amount")
    method = data.get("method")  # jazzcash / easypaisa
    transaction_id = data.get("transaction_id")

    if not clinic_id:
        raise HTTPException(status_code=400, detail="clinic_id required")

    payment = Payment(
        clinic_id=clinic_id,
        amount=amount,
        provider=method,
        transaction_id=transaction_id,
        status="pending"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment submitted successfully",
        "payment_id": payment.id,
        "status": payment.status
    }


# =========================
# ADMIN: VIEW ALL PAYMENTS
# =========================
@router.get("/payments")
def get_payments(db: Session = Depends(get_db)):

    payments = db.query(Payment).all()

    return payments


# =========================
# ADMIN: APPROVE PAYMENT
# =========================
@router.post("/approve/{payment_id}")
def approve_payment(payment_id: int, db: Session = Depends(get_db)):

    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    clinic = db.query(Clinic).filter(
        Clinic.id == payment.clinic_id
    ).first()

    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    # =========================
    # ACTIVATE PLAN
    # =========================
    clinic.subscription_status = "active"

    if clinic.plan == "trial":
        clinic.max_users = 1
    elif clinic.plan == "basic":
        clinic.max_users = 2
    elif clinic.plan == "pro":
        clinic.max_users = 5

    payment.status = "approved"

    db.commit()

    return {
        "message": "Payment approved successfully",
        "clinic_id": clinic.id,
        "plan": clinic.plan,
        "max_users": clinic.max_users
    }


# =========================
# ADMIN: REJECT PAYMENT
# =========================
@router.post("/reject/{payment_id}")
def reject_payment(payment_id: int, db: Session = Depends(get_db)):

    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = "rejected"

    db.commit()

    return {
        "message": "Payment rejected",
        "payment_id": payment.id
    }