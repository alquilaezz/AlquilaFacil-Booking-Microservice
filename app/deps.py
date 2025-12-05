from dataclasses import dataclass
from fastapi import Depends, Header, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from .database import SessionLocal
from .security import decode_token

# ---- DB ----

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- Current user ----

@dataclass
class CurrentUser:
    id: int
    role: str

def get_current_user(authorization: str = Header(...)) -> CurrentUser:
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header",
        )

    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = int(payload.get("sub"))
    role = payload.get("role", "USER")
    return CurrentUser(id=user_id, role=role)
