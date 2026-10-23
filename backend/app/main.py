from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.onboarding import router as onboarding_router
from app.api.copilot import router as copilot_router
from app.api.dashboard import router as dashboard_router
from app.api.knowledge import router as knowledge_router
from app.core.database import (
    Base,
    engine,
    test_database_connection
)
from app.models.user import User
from app.models.cloudprofile import UserCloudProfile
from app.models.knowledge import (
    KnowledgePost,
    KnowledgeComment,
    KnowledgeRating
)
from app.models.operation_result import CloudOperationResult
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Cloudwise AI API",
    description="Backend API for Cloudwise AI",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(auth_router)
app.include_router(knowledge_router)
app.include_router(onboarding_router)
app.include_router(copilot_router)
app.include_router(dashboard_router)
@app.get("/")
def root():
    return {
        "message": "Cloudwise AI API is running"
    }
@app.get("/api/health")
def health_check():
    try:
        test_database_connection()
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as error:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(error)
        }
