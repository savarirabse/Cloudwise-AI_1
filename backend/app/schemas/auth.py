from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    is_active: bool

class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    user: UserResponse
    
class RegisterResponse(BaseModel):
    message: str
    access_token: str
    token_type: str
    user: UserResponse