import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.document import MedicalDocument, DocumentType, OcrStatus
from app.models.health import HealthExpense, ExpenseCategory
from app.schemas.document import DocumentResponse, DocumentUploadResponse, AI_DISCLAIMER
from app.services.storage.s3 import upload_document
from app.worker.tasks import process_ocr_task
from datetime import date, timedelta

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document_endpoint(
    file: UploadFile = File(...),
    doc_type: DocumentType = Form(DocumentType.prescription),
    language: str = Form("en"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ("image/jpeg", "image/png", "image/webp", "image/heic"):
        raise HTTPException(status_code=400, detail="Only image files are accepted")

    contents = await file.read()
    s3_key = await upload_document(contents, str(current_user.id), file.filename or "upload.jpg")

    retention_until = date.today() + timedelta(days=7 * 365)
    doc = MedicalDocument(
        user_id=current_user.id,
        type=doc_type,
        raw_image_url=s3_key,
        ocr_status=OcrStatus.pending,
        language=language,
        retention_until=retention_until,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Kick off async OCR + AI processing
    process_ocr_task.apply_async(
        args=[str(doc.id)],
        queue="ocr",
        countdown=1,
    )

    return DocumentUploadResponse(id=doc.id, ocr_status=OcrStatus.pending)


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    doc_type: DocumentType | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(MedicalDocument).where(MedicalDocument.user_id == current_user.id)
    if doc_type:
        query = query.where(MedicalDocument.type == doc_type)
    query = query.order_by(MedicalDocument.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MedicalDocument).where(
            MedicalDocument.id == doc_id,
            MedicalDocument.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/{doc_id}/summary")
async def get_ai_summary(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MedicalDocument).where(
            MedicalDocument.id == doc_id,
            MedicalDocument.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.ocr_status != OcrStatus.completed:
        return {"status": doc.ocr_status, "message": "Document still processing"}

    return {
        "summary": (doc.ai_summary or "") + AI_DISCLAIMER,
        "confidence": doc.ai_confidence,
        "sources": doc.ai_sources or [],
        "structured_data": doc.structured_data,
    }


@router.delete("/{doc_id}", status_code=204)
async def delete_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MedicalDocument).where(
            MedicalDocument.id == doc_id,
            MedicalDocument.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(doc)
    await db.commit()
