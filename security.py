from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os

# ✅ SAME SECRET AS auth.py
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")
ALGORITHM = "HS256"

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):

    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        print("TOKEN PAYLOAD:", payload)

        return {
            "user_id": payload.get("user_id"),
            "role": payload.get("role"),
            "clinic_id": payload.get("clinic_id")
        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )