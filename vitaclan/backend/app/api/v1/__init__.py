from fastapi import APIRouter
from app.api.v1.routes import auth, documents, families, medications, voice, emergency, expenses, webhooks

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(documents.router)
router.include_router(families.router)
router.include_router(medications.router)
router.include_router(voice.router)
router.include_router(emergency.router)
router.include_router(expenses.router)
router.include_router(webhooks.router)
