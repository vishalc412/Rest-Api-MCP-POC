import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
import enum


class FamilyMemberRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
    view_only = "view-only"


class Family(Base):
    __tablename__ = "families"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FamilyMember(Base):
    __tablename__ = "family_members"

    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role: Mapped[FamilyMemberRole] = mapped_column(
        Enum(FamilyMemberRole, name="family_member_role"),
        nullable=False,
        default=FamilyMemberRole.member,
    )
    # {"hide_from": ["user_id_1", "user_id_2"]}
    privacy: Mapped[dict] = mapped_column(JSONB, default=dict)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
