from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserResponse
)
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse
)
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)
security = HTTPBearer()
@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match."
        )
    existing_user = db.scalar(
        select(User).where(User.email == request.email.lower())
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists."
        )
    new_user = User(
        first_name=request.first_name.strip(),
        last_name=request.last_name.strip(),
        email=request.email.lower(),
        phone=request.phone.strip(),
        password_hash=hash_password(request.password),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_access_token(new_user.id)
    return {
        "message": "Account created successfully.",
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }
@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.scalar(
        select(User).where(
            User.email == request.email.lower()
        )
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    if not verify_password(
        request.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive."
        )
    access_token = create_access_token(user.id)
    return {
        "message": "Login successful.",
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
@router.get(
    "/me",
    response_model=UserResponse
)
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user_id = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token."
        )
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive."
        )
    return user
@router.post("/logout")
def logout():
    return {
        "message": "Logout successful."
    }