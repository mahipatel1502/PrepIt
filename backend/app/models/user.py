from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserSignup(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if not v.strip():
            raise ValueError('Full name cannot be empty')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (max 72 bytes)')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    full_name: str
    email: str
    created_at: str
    
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
    
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    
class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=72)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password is too long (max 72 bytes)')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v
