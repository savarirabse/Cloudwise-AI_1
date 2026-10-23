from pydantic import BaseModel, Field

class OnboardingRequest(BaseModel):
    organization_name: str = Field(
        min_length=1,
        max_length=255
    )
    industry: str = Field(
        min_length=1,
        max_length=100
    )
    organization_size: str = Field(
        min_length=1,
        max_length=100
    )
    cloud_platforms: list[str] = Field(
        min_length=1
    )
    cloud_usage: str = Field(
        min_length=1,
        max_length=100
    )
    goals: list[str] = Field(
        min_length=1
    )
class OnboardingResponse(BaseModel):
    message: str
    profile_id: int