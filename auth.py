from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import os


from database import SessionLocal
from models import User, ClinicPlan, Clinic
from schemas import UserCreate, UserLogin


router = APIRouter()


# ================= SECURITY =================
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2


pwd_context = CryptContext(
   schemes=["pbkdf2_sha256"],
   deprecated="auto"
)


# ================= DB =================
def get_db():
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()


# ================= PASSWORD =================
def hash_password(password: str):
   return pwd_context.hash(password)


def verify_password(password: str, hashed: str):
   return pwd_context.verify(password, hashed)


# ================= TOKEN =================
def create_access_token(data: dict):
   to_encode = data.copy()
   expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
   to_encode.update({"exp": expire})
   return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ================= PLAN LIMITS =================
def get_max_users(plan: str):
   if plan == "trial":
       return 1
   elif plan == "basic":
       return 2
   elif plan == "pro":
       return 5
   return 1


# ================= REGISTER =================
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):


   username = user.username.strip()
   password = user.password.strip()[:72]
   role = user.role.strip().lower()
   clinic_name = user.clinic_name.strip()


   # ================= VALIDATION =================
   if len(username) < 3:
       raise HTTPException(status_code=400, detail="Username too short")


   if len(password) < 4:
       raise HTTPException(status_code=400, detail="Password too short")


   if role not in ["admin", "doctor", "patient"]:
       raise HTTPException(status_code=400, detail="Invalid role")


   # ================= CHECK USER =================
   existing_user = db.query(User).filter(User.username == username).first()
   if existing_user:
       raise HTTPException(status_code=400, detail="User already exists")


   # ================= CHECK OR CREATE CLINIC =================
   clinic = db.query(Clinic).filter(Clinic.name == clinic_name).first()


   # IF CLINIC DOES NOT EXIST → CREATE IT
   if not clinic:
       clinic = Clinic(
           name=clinic_name,
           plan="trial",
           max_users=1,
           subscription_status="trialing"
       )
       db.add(clinic)
       db.commit()
       db.refresh(clinic)


   # ================= ENFORCE USER LIMIT =================
   current_users = db.query(User).filter(
       User.clinic_id == clinic.id
   ).count()


   max_allowed = get_max_users(clinic.plan)


   if current_users >= max_allowed:
       raise HTTPException(
           status_code=400,
           detail=f"User limit reached for {clinic.plan} plan"
       )


   # ================= CREATE USER =================
   new_user = User(
       username=username,
       password=hash_password(password),
       role=role,
       clinic_id=clinic.id
   )


   db.add(new_user)
   db.commit()
   db.refresh(new_user)


   return {
       "message": "User created successfully",
       "clinic_id": clinic.id,
       "user_id": new_user.id,
       "role": new_user.role,
       "plan": clinic.plan,
       "users_used": current_users + 1,
       "max_users": max_allowed
   }


# ================= LOGIN =================
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):


   username = user.username.strip()
   password = user.password.strip()


   db_user = db.query(User).filter(User.username == username).first()


   if not db_user:
       raise HTTPException(status_code=400, detail="Invalid credentials")


   if not verify_password(password, db_user.password):
       raise HTTPException(status_code=400, detail="Invalid credentials")
   clinic = db.query(Clinic).filter(Clinic.id == db_user.clinic_id).first()

   if not clinic:
       raise HTTPException(status_code=400, detail="Clinic not found")

   if clinic.subscription_status == "blocked":
       raise HTTPException(
           status_code=403,
           detail="Subscription blocked. Please contact admin."
       )

   # allow trial + active users
   if clinic.subscription_status not in ["trialing", "active"]:
       raise HTTPException(
           status_code=403,
           detail="Subscription inactive. Please complete payment or wait for approval."
       )

   token = create_access_token({
       "user_id": db_user.id,
       "role": db_user.role,
       "clinic_id": db_user.clinic_id
   })


   return {
       "access_token": token,
       "token_type": "bearer",
       "user_id": db_user.id,
       "role": db_user.role,
       "clinic_id": db_user.clinic_id
   }
