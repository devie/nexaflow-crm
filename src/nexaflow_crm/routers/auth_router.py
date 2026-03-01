from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from nexaflow_crm.auth import create_access_token, get_current_user, hash_password, verify_password
from nexaflow_crm.database import get_db
from nexaflow_crm.models import User
from nexaflow_crm.schemas import LoginRequest, Token, UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=Token)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, name=data.name, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return Token(access_token=create_access_token(user.id))


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.put("/me", response_model=UserOut)
def update_me(data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.name is not None:
        user.name = data.name
    if data.email is not None:
        existing = db.query(User).filter(User.email == data.email, User.id != user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = data.email
    if data.password is not None:
        user.hashed_password = hash_password(data.password)
    if data.preferred_currency is not None:
        user.preferred_currency = data.preferred_currency
    db.commit()
    db.refresh(user)
    return user
