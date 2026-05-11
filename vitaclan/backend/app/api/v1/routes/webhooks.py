from fastapi import APIRouter, Request, HTTPException
from app.core.config import settings

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.get("/whatsapp")
async def whatsapp_verify(request: Request):
    """Meta webhook verification handshake."""
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge", 0))
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/whatsapp")
async def whatsapp_inbound(request: Request):
    """Handle inbound WhatsApp messages (voice notes, document shares)."""
    body = await request.json()
    # TODO: parse incoming messages and route to appropriate handlers
    # e.g., voice notes → transcribe → save as VoiceNote
    # e.g., image → save as MedicalDocument → trigger OCR
    return {"status": "received"}
