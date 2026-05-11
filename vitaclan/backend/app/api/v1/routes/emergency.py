import uuid
import io
import qrcode
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.health import HealthProfile
from app.models.medication import Medication
from app.services.ai.emergency_pdf import generate_emergency_pdf

router = APIRouter(prefix="/emergency", tags=["emergency"])


@router.get("/{user_id}/qr")
async def get_emergency_qr(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    summary = await _build_emergency_summary(db, user_id)

    # QR encodes a compact JSON summary
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(str(summary))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.get("/{user_id}/pdf")
async def get_emergency_pdf(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    summary = await _build_emergency_summary(db, user_id)
    pdf_bytes = generate_emergency_pdf(summary)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=emergency_{user_id}.pdf"},
    )


async def _build_emergency_summary(db: AsyncSession, user_id: uuid.UUID) -> dict:
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    profile_result = await db.execute(
        select(HealthProfile).where(HealthProfile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()

    meds_result = await db.execute(
        select(Medication).where(Medication.user_id == user_id, Medication.is_active == True)
    )
    active_meds = meds_result.scalars().all()

    return {
        "name": user.name if user else "Unknown",
        "phone": user.phone if user else "",
        "blood_group": profile.blood_group if profile else "Unknown",
        "allergies": profile.allergies if profile else [],
        "conditions": profile.conditions if profile else [],
        "active_medications": [
            {"name": m.name, "dosage": m.dosage, "frequency": m.frequency}
            for m in active_meds
        ],
    }
