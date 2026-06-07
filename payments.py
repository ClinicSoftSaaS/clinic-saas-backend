from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Payment, User

router = APIRouter()

# ================= DB =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= USER: SUBMIT PAYMENT =================
@router.post("/submit-payment")
def submit_payment(data: dict, db: Session = Depends(get_db)):

    payment = Payment(
        clinic_id=data["clinic_id"],
        plan=data["plan"],
        amount=data["amount"],
        screenshot_url=data["screenshot_url"],
        status="pending"
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {"message": "Payment submitted successfully"}


# ================= ADMIN: GET ALL PAYMENTS =================
@router.get("/all-payments")
def get_payments(db: Session = Depends(get_db)):
    return db.query(Payment).all()


# ================= ADMIN: APPROVE PAYMENT =================
@router.post("/approve-payment/{payment_id}")
def approve_payment(payment_id: int, db: Session = Depends(get_db)):

    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        return {"error": "Payment not found"}

    payment.status = "approved"

    # activate user / clinic
    user = db.query(User).filter(User.id == payment.clinic_id).first()

    if user:
        user.is_active = True
        user.plan = payment.plan

    db.commit()

    return {"message": "Payment approved and plan activated"}