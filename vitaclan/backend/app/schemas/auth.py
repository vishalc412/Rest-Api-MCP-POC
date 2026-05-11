from pydantic import BaseModel, field_validator
import re


class SendOtpRequest(BaseModel):
    phone: str
    consent_given: bool = True

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if not (10 <= len(cleaned) <= 12):
            raise ValueError("Invalid phone number")
        return f"+91{cleaned[-10:]}" if len(cleaned) == 10 else f"+{cleaned}"


class VerifyOtpRequest(BaseModel):
    phone: str
    code: str
    name: str | None = None
    language: str = "en"

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        return f"+91{cleaned[-10:]}" if len(cleaned) == 10 else f"+{cleaned}"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    is_new_user: bool
