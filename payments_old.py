import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import SessionLocal
from models import Payment, ClinicPlan, Clinic   # make sure Clinic exists in models

# ================= LOAD ENV =================
load_dotenv()

router = APIRouter(prefix="/payments", tags=["Payments"])


# ================= DB SESSION =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================
# 1. CREATE PAYMENT (USER INITIATES PAYMENT)
# =====================================================
@router.post("/create")
def create_payment(data: dict, db: Session = Depends(get_db)):

    payment = Payment(
        clinic_id=data["clinic_id"],
        amount=data["amount"],
        currency=data.get("currency", "PKR"),
        provider=data.get("provider", "jazzcash"),
        status="pending"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment created successfully",
        "payment_id": payment.id,
        "status": payment.status
    }


# =====================================================
# 2. SUBMIT PAYMENT PROOF (USER AFTER PAYING)
# =====================================================
@router.post("/submit-proof")
def submit_payment_proof(data: dict, db: Session = Depends(get_db)):

    payment = db.query(Payment).filter(Payment.id == data["payment_id"]).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.proof_url = data.get("proof_url")
    payment.transaction_id = data.get("transaction_id")
    payment.status = "pending_verification"

    db.commit()

    return {
        "message": "Payment proof submitted successfully",
        "status": payment.status
    }


# =====================================================
# 3. ADMIN APPROVE PAYMENT
# =====================================================
@router.post("/admin/approve/{payment_id}")
def approve_payment(payment_id: int, db: Session = Depends(get_db)):

    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = "paid"

    # Activate clinic
    clinic = db.query(Clinic).filter(Clinic.id == payment.clinic_id).first()

    if clinic:
        clinic.status = "active"

    # Upgrade plan
    plan_record = db.query(ClinicPlan).filter(
        ClinicPlan.clinic_id == payment.clinic_id
    ).first()

    if plan_record:
        if payment.amount <= 2000:
            plan_record.plan_name = "basic"
            plan_record.max_users = 2

        elif payment.amount <= 5000:
            plan_record.plan_name = "pro"
            plan_record.max_users = 5

        else:
            plan_record.plan_name = "premium"
            plan_record.max_users = 10

    db.commit()

    return {
        "message": "Payment approved successfully",
        "clinic_status": "active"
    }


# =====================================================
# 4. ADMIN REJECT PAYMENT
# =====================================================
@router.post("/admin/reject/{payment_id}")
def reject_payment(payment_id: int, db: Session = Depends(get_db)):

    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = "rejected"

    db.commit()

    return {
        "message": "Payment rejected successfully",
        "status": payment.status
    }


# =====================================================
# 5. GET ALL PAYMENTS (FOR ADMIN DASHBOARD)
# =====================================================
@router.get("/all")
def get_all_payments(db: Session = Depends(get_db)):

    payments = db.query(Payment).all()

    return payments


# =====================================================
# 6. GET PENDING PAYMENTS (FOR ADMIN)
# =====================================================
@router.get("/pending")
def get_pending_payments(db: Session = Depends(get_db)):

    payments = db.query(Payment).filter(
        Payment.status.in_(["pending", "pending_verification"])
    ).all()

    return payments