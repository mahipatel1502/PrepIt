from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional

class UserSignup(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)  # Firebase requires min 6 characters
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if not v.strip():
            raise ValueError('Full name cannot be empty')
        return v.strip()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    email_verified: bool = False
    
class TokenResponse(BaseModel):
    id_token: str
    refresh_token: str
    expires_in: int
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
    
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    
class PasswordChange(BaseModel):
    new_password: str = Field(..., min_length=6)  # Firebase requires min 6 characters
