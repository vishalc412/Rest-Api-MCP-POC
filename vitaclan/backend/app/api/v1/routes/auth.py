import random
import string
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import create_access_token
from app.core.config import settings
from app.models.user import User
from app.models.audit import OtpCode, AuditLog
from app.schemas.auth import SendOtpRequest, VerifyOtpRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


@router.post("/send-otp", status_code=200)
async def send_otp(body: SendOtpRequest, db: AsyncSession = Depends(get_db)):
    otp = _generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    db.add(OtpCode(phone=body.phone, code=otp, expires_at=expires_at))
    await db.commit()

    # In production: send via Firebase Auth / SMS gateway
    # For dev: return OTP directly (remove in prod!)
    if settings.ENVIRONMENT == "development":
        return {"message": f"OTP sent to {body.phone}", "dev_otp": otp}
    return {"message": f"OTP sent to {body.phone}"}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(body: VerifyOtpRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OtpCode).where(
            OtpCode.phone == body.phone,
            OtpCode.code == body.code,
            OtpCode.used == False,
            OtpCode.expires_at > datetime.now(timezone.utc),
        ).order_by(OtpCode.created_at.desc())
    )
    otp_record = result.scalar_one_or_none()
    if not otp_record:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    otp_record.used = True

    user_result = await db.execute(
        select(User).where(User.phone == body.phone, User.deleted_at.is_(None))
    )
    user = user_result.scalar_one_or_none()
    is_new_user = user is None

    if is_new_user:
        user = User(
            phone=body.phone,
            name=body.name or body.phone,
            language=body.language,
            consent_given_at=datetime.now(timezone.utc),
        )
        db.add(user)

    db.add(AuditLog(
        user_id=user.id if not is_new_user else None,
        action="login" if not is_new_user else "register",
        resource="user",
        ip_address=request.client.host if request.client else None,
    ))

    await db.commit()
    await db.refresh(user)

    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token, user_id=str(user.id), is_new_user=is_new_user)


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    db: AsyncSession = Depends(get_db),
    # Uses current user from bearer token
):
    # Handled at deps level; simply issue a new token
    raise HTTPException(status_code=501, detail="Use /verify-otp to re-authenticate")
