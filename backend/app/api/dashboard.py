
from datetime import datetime
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.cloudprofile import UserCloudProfile
from app.models.operation_result import CloudOperationResult

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)
security = HTTPBearer()
class CloudReadinessAssessment(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    categories: dict[str, int]
    answers: dict = Field(default_factory=dict)
class CostOptimizationCalculation(BaseModel):
    currency: str = Field(min_length=1, max_length=10)
    monthly_bill: float = Field(ge=0)
    monthly_savings: float = Field(ge=0)
    annual_savings: float = Field(ge=0)
    monthly_savings_percent: float = Field(ge=0, le=100)
    optimization_percent: float = Field(ge=0, le=100)
    inputs: dict = Field(default_factory=dict)
def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials,
    db: Session
):
    try:
        user_id = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )
    return user
@router.get("/profile")
def get_dashboard_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = get_authenticated_user(credentials, db)
    profile = (
        db.query(UserCloudProfile)
        .filter(UserCloudProfile.user_id == user.id)
        .first()
    )
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Cloud profile not found"
        )
    try:
        cloud_platforms = json.loads(profile.cloud_platforms)
    except (TypeError, ValueError):
        cloud_platforms = profile.cloud_platforms
    try:
        goals = json.loads(profile.goals)
    except (TypeError, ValueError):
        goals = profile.goals
    return {
        "user": {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone
        },
        "organization": {
            "name": profile.organization_name,
            "industry": profile.industry,
            "size": profile.organization_size
        },
        "cloud": {
            "platforms": cloud_platforms,
            "usage": profile.cloud_usage,
            "goals": goals
        }
    }
@router.post("/calculations/cost-optimization")
def save_cost_optimization(
    payload: CostOptimizationCalculation,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = get_authenticated_user(credentials, db)
    result_data = {
        "currency": payload.currency,
        "monthly_bill": payload.monthly_bill,
        "monthly_savings": payload.monthly_savings,
        "annual_savings": payload.annual_savings,
        "monthly_savings_percent": payload.monthly_savings_percent,
        "optimization_percent": payload.optimization_percent,
        "inputs": payload.inputs
    }
    record = CloudOperationResult(
        user_id=user.id,
        operation_type="cost_optimization",
        result=result_data
    )
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
        return {
            "message": "Cost optimization result saved",
            "operation_type": record.operation_type,
            "created_at": record.created_at.isoformat()
        }
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to save calculation"
        )
@router.get("/calculations/latest")
def get_latest_calculations(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = get_authenticated_user(credentials, db)
    records = (
        db.query(CloudOperationResult)
        .filter(CloudOperationResult.user_id == user.id)
        .order_by(
            CloudOperationResult.created_at.desc(),
            CloudOperationResult.id.desc()
        )
        .all()
    )
    latest_by_operation = {}
    for record in records:
        if record.operation_type not in latest_by_operation:
            latest_by_operation[record.operation_type] = {
                "operation_type": record.operation_type,
                "result": record.result,
                "created_at": record.created_at.isoformat()
            }

    return {
        "results": list(latest_by_operation.values())
    }
@router.post("/readiness")
def save_cloud_readiness(
    payload: CloudReadinessAssessment,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Save the current SkyReady assessment for the authenticated user."""
    user = get_authenticated_user(credentials, db)
    category_names = {"Compute", "Data", "Network", "Security", "People"}
    if set(payload.categories.keys()) != category_names:
        raise HTTPException(
            status_code=422,
            detail="Categories must include Compute, Data, Network, Security, and People"
        )
    result_data = {
        "overall_score": payload.overall_score,
        "categories": {
            name: int(max(0, min(100, score)))
            for name, score in payload.categories.items()
        },
        "answers": payload.answers
    }
    record = CloudOperationResult(
        user_id=user.id,
        operation_type="cloud_readiness",
        result=result_data
    )
    try:
        db.add(record)
        db.commit()
        db.refresh(record)
        return {
            "message": "Cloud readiness assessment saved",
            "operation_type": record.operation_type,
            "created_at": record.created_at.isoformat()
        }
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to save cloud readiness assessment")
@router.get("/readiness/latest")
def get_latest_cloud_readiness(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Return latest assessment and saved assessment history for the authenticated user."""
    user = get_authenticated_user(credentials, db)
    records = (
        db.query(CloudOperationResult)
        .filter(
            CloudOperationResult.user_id == user.id,
            CloudOperationResult.operation_type == "cloud_readiness"
        )
        .order_by(CloudOperationResult.created_at.asc(), CloudOperationResult.id.asc())
        .all()
    )
    history = [
        {
            "overall_score": record.result.get("overall_score", 0),
            "categories": record.result.get("categories", {}),
            "created_at": record.created_at.isoformat()
        }
        for record in records
    ]
    return {
        "latest": history[-1] if history else None,
        "history": history
    }
