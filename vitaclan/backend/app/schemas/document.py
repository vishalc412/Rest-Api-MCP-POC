import uuid
from datetime import datetime, date
from pydantic import BaseModel
from app.models.document import DocumentType, OcrStatus


class DocumentUploadResponse(BaseModel):
    id: uuid.UUID
    ocr_status: OcrStatus
    message: str = "Document uploaded. OCR processing started."


class MedicineItem(BaseModel):
    name: str
    dosage: str | None = None
    frequency: str | None = None
    instructions: str | None = None


class TestResult(BaseModel):
    name: str
    result: str | None = None
    unit: str | None = None
    normal_range: str | None = None


class CostBreakdown(BaseModel):
    item: str
    amount: float


class StructuredData(BaseModel):
    medicines: list[MedicineItem] = []
    tests: list[TestResult] = []
    cost: dict | None = None
    doctor: str | None = None
    hospital: str | None = None
    date: str | None = None


class DocumentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    type: DocumentType
    ocr_status: OcrStatus
    structured_data: StructuredData | None = None
    ai_summary: str | None = None
    ai_confidence: float | None = None
    ai_sources: list[str] | None = None
    language: str
    document_date: date | None = None
    doctor_name: str | None = None
    hospital_name: str | None = None
    created_at: datetime
    raw_image_url: str

    model_config = {"from_attributes": True}


AI_DISCLAIMER = (
    "\n\n⚠️ Disclaimer: This information is for educational purposes only and is NOT medical advice. "
    "Please consult a qualified healthcare professional for diagnosis, treatment, or any medical decisions."
)
