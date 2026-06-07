from database import SessionLocal
from models import Clinic

db = SessionLocal()

clinic = Clinic(
    name="Ali Dental"
)

db.add(clinic)
db.commit()
db.refresh(clinic)

print("Clinic created:", clinic.id)