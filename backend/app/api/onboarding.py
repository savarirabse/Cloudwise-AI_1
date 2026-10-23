import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.cloudprofile import UserCloudProfile
from app.schemas.onboarding import (
    OnboardingRequest,
    OnboardingResponse
)
router = APIRouter(
    prefix="/api/onboarding",
    tags=["Onboarding"]
)
security = HTTPBearer()
@router.post(
    "",
    response_model=OnboardingResponse,
    status_code=status.HTTP_201_CREATED
)
def save_onboarding(
    request: OnboardingRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user_id = decode_access_token(
            credentials.credentials
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token."
        )
    existing_profile = db.scalar(
        select(UserCloudProfile).where(
            UserCloudProfile.user_id == user_id
        )
    )
    if existing_profile:
        existing_profile.organization_name = (
            request.organization_name.strip()
        )
        existing_profile.industry = (
            request.industry.strip()
        )
        existing_profile.organization_size = (
            request.organization_size.strip()
        )
        existing_profile.cloud_platforms = json.dumps(
            request.cloud_platforms
        )
        existing_profile.cloud_usage = (
            request.cloud_usage.strip()
        )
        existing_profile.goals = json.dumps(
            request.goals
        )
        db.commit()
        db.refresh(existing_profile)
        return {
            "message": "Onboarding information updated successfully.",
            "profile_id": existing_profile.id
        }
    profile = UserCloudProfile(
        user_id=user_id,
        organization_name=request.organization_name.strip(),
        industry=request.industry.strip(),
        organization_size=request.organization_size.strip(),
        cloud_platforms=json.dumps(
            request.cloud_platforms
        ),
        cloud_usage=request.cloud_usage.strip(),
        goals=json.dumps(
            request.goals
        )
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {
        "message": "Onboarding information saved successfully.",
        "profile_id": profile.id
    }