import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.family import FamilyMemberRole


class FamilyCreate(BaseModel):
    name: str


class FamilyResponse(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class InviteMemberRequest(BaseModel):
    phone: str
    role: FamilyMemberRole = FamilyMemberRole.member


class UpdatePrivacyRequest(BaseModel):
    hide_from: list[str] = []  # list of user_id strings


class FamilyMemberResponse(BaseModel):
    user_id: uuid.UUID
    family_id: uuid.UUID
    role: FamilyMemberRole
    privacy: dict
    joined_at: datetime

    model_config = {"from_attributes": True}
