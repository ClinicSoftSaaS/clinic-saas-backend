from fastapi import HTTPException
from models import Clinic


def check_subscription(db, clinic_id):

    clinic = db.query(Clinic).filter(
        Clinic.id == clinic_id
    ).first()

    if not clinic:
        raise HTTPException(
            status_code=404,
            detail="Clinic not found"
        )

    # ACTIVE ACCESS
    if clinic.subscription_status == "blocked":
        raise HTTPException(
            status_code=403,
            detail="Account blocked"
        )

    return clinic