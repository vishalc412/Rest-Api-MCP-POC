"""
Voice query engine — answers natural language health questions using the user's data.
"When was my last blood test?" → queries DB → formats answer via LLM.
"""
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_ollama import OllamaLLM
from app.core.config import settings
from app.models.document import MedicalDocument, OcrStatus
from app.models.medication import Medication
from app.models.health import HealthProfile


QUERY_SYSTEM_PROMPT = """You are VitaClan's health assistant. Answer questions about the user's health records.

Rules:
- Only answer based on the provided health data context
- If information is not in the context, say "I don't have that information in your records"
- Keep answers brief and conversational
- Never diagnose or prescribe
- For dates, use DD Month YYYY format (e.g., 15 March 2025)"""


async def answer_health_query(
    user_id: str,
    query: str,
    language: str,
    db: AsyncSession,
) -> str:
    context = await _build_user_context(user_id, db)
    lang_name = "Hindi" if language == "hi" else "English"

    prompt = f"""{QUERY_SYSTEM_PROMPT}

User's health data:
{context}

User question (answer in {lang_name}): {query}"""

    try:
        llm = OllamaLLM(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_LLM_MODEL,
            temperature=0.2,
        )
        return str(llm.invoke(prompt))
    except Exception as e:
        return f"Sorry, I couldn't process your query right now. Please try again. ({str(e)})"


async def _build_user_context(user_id: str, db: AsyncSession) -> str:
    uid = uuid.UUID(user_id)
    cutoff = datetime.now(timezone.utc) - timedelta(days=180)

    # Recent documents
    docs_result = await db.execute(
        select(MedicalDocument)
        .where(
            MedicalDocument.user_id == uid,
            MedicalDocument.ocr_status == OcrStatus.completed,
            MedicalDocument.created_at >= cutoff,
        )
        .order_by(MedicalDocument.created_at.desc())
        .limit(20)
    )
    docs = docs_result.scalars().all()

    # Active medications
    meds_result = await db.execute(
        select(Medication).where(Medication.user_id == uid, Medication.is_active == True)
    )
    meds = meds_result.scalars().all()

    # Health profile
    profile_result = await db.execute(
        select(HealthProfile).where(HealthProfile.user_id == uid)
    )
    profile = profile_result.scalar_one_or_none()

    lines = []

    if profile:
        lines.append(f"Blood group: {profile.blood_group or 'Not recorded'}")
        if profile.conditions:
            lines.append(f"Known conditions: {', '.join(profile.conditions)}")
        if profile.allergies:
            lines.append(f"Allergies: {', '.join(profile.allergies)}")

    if meds:
        lines.append("\nCurrent medications:")
        for m in meds:
            lines.append(f"  - {m.name} {m.dosage or ''} {m.frequency or ''}")

    if docs:
        lines.append("\nRecent health records:")
        for d in docs:
            date_str = d.document_date.strftime("%d %B %Y") if d.document_date else d.created_at.strftime("%d %B %Y")
            lines.append(f"  - [{date_str}] {d.type.value}: {d.doctor_name or ''} @ {d.hospital_name or 'Unknown hospital'}")
            if d.structured_data and d.structured_data.get("tests"):
                for t in d.structured_data["tests"][:3]:
                    lines.append(f"      Test: {t.get('name')} = {t.get('result')} {t.get('unit', '')}")

    return "\n".join(lines) if lines else "No health records found."
