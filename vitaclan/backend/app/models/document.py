import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, DateTime, ForeignKey, func, Enum, Date, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class DocumentType(str, enum.Enum):
    prescription = "prescription"
    lab_report = "lab_report"
    bill = "bill"
    doctor_note = "doctor_note"
    other = "other"


class OcrStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class MedicalDocument(Base):
    __tablename__ = "medical_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    family_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("families.id"))
    type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType, name="document_type"),
        nullable=False,
        default=DocumentType.other,
    )
    raw_image_url: Mapped[str] = mapped_column(Text, nullable=False)  # S3 key
    ocr_text: Mapped[str | None] = mapped_column(Text)
    # {medicines:[{name,dosage,frequency}], tests:[{name,result,unit,normal_range}], cost:{total,breakdown}, doctor, hospital}
    structured_data: Mapped[dict | None] = mapped_column(JSONB)
    ai_summary: Mapped[str | None] = mapped_column(Text)
    ai_confidence: Mapped[float | None] = mapped_column(Float)
    ai_sources: Mapped[list | None] = mapped_column(JSONB)
    ocr_status: Mapped[OcrStatus] = mapped_column(
        Enum(OcrStatus, name="ocr_status"),
        default=OcrStatus.pending,
    )
    language: Mapped[str] = mapped_column(String(10), default="en")
    document_date: Mapped[date | None] = mapped_column(Date)
    doctor_name: Mapped[str | None] = mapped_column(String(255))
    hospital_name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    retention_until: Mapped[date | None] = mapped_column(Date)
