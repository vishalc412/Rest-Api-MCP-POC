import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, DateTime, ForeignKey, func, Enum, Date, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, ARRAY, TEXT, JSONB
from app.core.database import Base


class ExpenseCategory(str, enum.Enum):
    doctor_fee = "doctor_fee"
    lab_test = "lab_test"
    medicine = "medicine"
    other = "other"


class HealthProfile(Base):
    __tablename__ = "health_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    blood_group: Mapped[str | None] = mapped_column(String(5))
    allergies: Mapped[list | None] = mapped_column(ARRAY(TEXT))
    conditions: Mapped[list | None] = mapped_column(ARRAY(TEXT))
    emergency_summary: Mapped[dict | None] = mapped_column(JSONB)  # pre-computed for QR/PDF
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class HealthExpense(Base):
    __tablename__ = "health_expenses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    document_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("medical_documents.id"))
    amount: Mapped[float | None] = mapped_column(Numeric(10, 2))
    category: Mapped[ExpenseCategory] = mapped_column(
        Enum(ExpenseCategory, name="expense_category"),
        default=ExpenseCategory.other,
    )
    expense_date: Mapped[date | None] = mapped_column(Date)
    vendor_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class VoiceNote(Base):
    __tablename__ = "voice_notes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    transcription: Mapped[str | None] = mapped_column(Text)
    audio_url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
