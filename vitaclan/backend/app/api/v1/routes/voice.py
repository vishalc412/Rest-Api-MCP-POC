from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.health import VoiceNote
from app.schemas.document import AI_DISCLAIMER
from app.services.ai.voice_query import answer_health_query

router = APIRouter(prefix="/voice", tags=["voice"])


class VoiceQueryRequest(BaseModel):
    query: str
    language: str = "en"


class VoiceNoteRequest(BaseModel):
    transcription: str


@router.post("/query")
async def voice_query(
    body: VoiceQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    answer = await answer_health_query(
        user_id=str(current_user.id),
        query=body.query,
        language=body.language,
        db=db,
    )
    return {
        "query": body.query,
        "answer": answer + AI_DISCLAIMER,
    }


@router.post("/note", status_code=201)
async def save_voice_note(
    body: VoiceNoteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    note = VoiceNote(user_id=current_user.id, transcription=body.transcription)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return {"id": str(note.id), "transcription": note.transcription}
