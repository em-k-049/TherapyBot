from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Literal

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class MessageCreate(BaseModel):
    session_id: UUID
    content: str

class MessageRead(BaseModel):
    id: UUID
    content: str
    created_at: datetime
    is_escalated: bool
    audio_data: str = None
    risk_score: float = None
    risk_tags: list = None
    
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    message: MessageRead
    ai_response: str = None
    ai_audio: str = None  # Base64 encoded audio

class RoleUpdate(BaseModel):
    role: Literal["patient", "consultant", "admin"]

class LoginRequest(BaseModel):
    username: str
    password: str
    otp_code: str = None

class TwoFASetup(BaseModel):
    secret: str
    qr_code: str

class TwoFAVerify(BaseModel):
    otp_code: str

class TTSRequest(BaseModel):
    text: str
    