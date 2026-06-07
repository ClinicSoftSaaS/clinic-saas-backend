from fastapi import Depends, HTTPException
from auth import get_current_user

def require_role(*allowed_roles):
    def dependency(user = Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Access denied: insufficient permissions"
            )
        return user
    return dependency