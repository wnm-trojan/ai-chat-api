from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: UUID | None = None
    model: str | None = None


class ChatResponse(BaseModel):
    conversation_id: UUID
    reply: str
    cached: bool
