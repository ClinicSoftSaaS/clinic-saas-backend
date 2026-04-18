from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import SessionLocal
from models import User
from schemas import UserCreate, UserLogin

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
# REGISTER USER
# =========================
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    username = (user.username or "").strip()
    password = (user.password or "").strip()
    role = (user.role or "").strip().lower()

    if not username or len(username) < 3:
        raise HTTPException(status_code=400, detail="Invalid username")

    if not password or len(password) < 4:
        raise HTTPException(status_code=400, detail="Invalid password")

    if role not in ["doctor", "patient"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(password)

    new_user = User(
        username=username,
        password=hashed_password,
        role=role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id,
        "role": new_user.role
    }


# =========================
# LOGIN USER
# =========================
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    username = (user.username or "").strip()
    password = (user.password or "").strip()

    db_user = db.query(User).filter(User.username == username).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not pwd_context.verify(password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user_id": db_user.id,
        "role": db_user.role
    }


# =========================
# TEST USER (FIXED)
# =========================
@router.post("/create-test")
def create_test_user(db: Session = Depends(get_db)):

    hashed_password = pwd_context.hash("1234")

    user = User(
        username="admin",
        password=hashed_password,
        role="doctor"
    )

    db.add(user)
    db.commit()

    return {"msg": "test user created"}