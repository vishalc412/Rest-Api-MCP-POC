"""
Celery tasks: OCR processing and medication reminders.
These run async outside the FastAPI request cycle.
"""
import uuid
import asyncio
from datetime import datetime, time, timezone
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.worker.celery_app import celery_app
from app.core.config import settings


def _get_sync_session():
    engine = create_engine(settings.SYNC_DATABASE_URL)
    return Session(engine)


@celery_app.task(name="app.worker.tasks.process_ocr_task", bind=True, max_retries=3)
def process_ocr_task(self, document_id: str):
    """
    Full OCR pipeline for a medical document:
    1. Download image from S3
    2. Run OCR cascade (LLaVA → Cloud Vision)
    3. Structure with Llama 70B
    4. Generate AI summary via RAG
    5. Extract expenses from bills
    6. Persist results
    """
    from app.models.document import MedicalDocument, OcrStatus, DocumentType
    from app.models.health import HealthExpense, ExpenseCategory
    from app.models.medication import Medication

    try:
        with _get_sync_session() as db:
            doc = db.get(MedicalDocument, uuid.UUID(document_id))
            if not doc:
                return {"error": "Document not found"}

            doc.ocr_status = OcrStatus.processing
            db.commit()

        # Run async OCR pipeline in sync context
        from app.services.ocr.pipeline import run_ocr_pipeline
        from app.services.storage.s3 import download_document
        from app.services.ai.interpreter import interpret_medical_document

        image_bytes = asyncio.run(download_document(doc.raw_image_url))
        structured_data, confidence, method = asyncio.run(
            run_ocr_pipeline(image_bytes, language=doc.language)
        )

        # Generate AI summary
        ai_summary, ai_confidence, sources = asyncio.run(
            interpret_medical_document(structured_data, language=doc.language)
        )

        with _get_sync_session() as db:
            doc = db.get(MedicalDocument, uuid.UUID(document_id))
            doc.structured_data = structured_data
            doc.ocr_text = structured_data.get("raw_text")
            doc.ai_summary = ai_summary
            doc.ai_confidence = ai_confidence
            doc.ai_sources = sources
            doc.ocr_status = OcrStatus.completed

            # Extract doctor/hospital from structured data
            if structured_data.get("doctor"):
                doc.doctor_name = structured_data["doctor"]
            if structured_data.get("hospital"):
                doc.hospital_name = structured_data["hospital"]
            if structured_data.get("date"):
                from datetime import date
                try:
                    doc.document_date = date.fromisoformat(structured_data["date"])
                except (ValueError, TypeError):
                    pass

            db.commit()

            # Auto-create medications from prescriptions
            if doc.type == DocumentType.prescription:
                for med_data in structured_data.get("medicines", []):
                    if med_data.get("name"):
                        existing = db.execute(
                            select(Medication).where(
                                Medication.user_id == doc.user_id,
                                Medication.name == med_data["name"],
                                Medication.is_active == True,
                            )
                        ).scalar_one_or_none()
                        if not existing:
                            db.add(Medication(
                                user_id=doc.user_id,
                                document_id=doc.id,
                                name=med_data["name"],
                                dosage=med_data.get("dosage"),
                                frequency=med_data.get("frequency"),
                                instructions=med_data.get("instructions"),
                            ))

            # Auto-create expenses from bills
            if doc.type == DocumentType.bill and structured_data.get("cost"):
                cost = structured_data["cost"]
                if cost.get("total"):
                    db.add(HealthExpense(
                        user_id=doc.user_id,
                        document_id=doc.id,
                        amount=cost["total"],
                        category=ExpenseCategory.other,
                        expense_date=doc.document_date,
                        vendor_name=doc.hospital_name,
                    ))

            db.commit()

        return {"status": "completed", "method": method, "confidence": confidence}

    except Exception as exc:
        with _get_sync_session() as db:
            doc = db.get(MedicalDocument, uuid.UUID(document_id))
            if doc:
                from app.models.document import OcrStatus
                doc.ocr_status = OcrStatus.failed
                db.commit()
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(name="app.worker.tasks.send_medication_reminders")
def send_medication_reminders():
    """
    Check all active medication reminders and send due notifications.
    Runs every minute via Celery Beat.
    """
    from app.models.medication import Medication, MedicationReminder, ReminderChannel
    from app.models.user import User

    now = datetime.now(timezone.utc)
    current_time = now.time()
    current_dow = now.weekday()  # 0=Mon in Python, adjust for 0=Sun convention

    with _get_sync_session() as db:
        reminders = db.execute(
            select(MedicationReminder)
            .join(Medication, MedicationReminder.medication_id == Medication.id)
            .where(
                MedicationReminder.is_active == True,
                Medication.is_active == True,
            )
        ).scalars().all()

        for reminder in reminders:
            # Check if this reminder fires now (within 1 minute window)
            reminder_time = reminder.schedule_time
            delta_seconds = abs(
                (datetime.combine(now.date(), current_time) -
                 datetime.combine(now.date(), reminder_time)).total_seconds()
            )
            if delta_seconds > 60:
                continue

            # Check day of week
            if reminder.days_of_week:
                # Convert Python Monday=0 to Sunday=0 convention
                dow = (current_dow + 1) % 7
                if dow not in reminder.days_of_week:
                    continue

            medication = db.get(Medication, reminder.medication_id)
            user = db.get(User, medication.user_id)

            if not user:
                continue

            msg = f"💊 Time for {medication.name} {medication.dosage or ''}. {medication.instructions or ''}"

            if reminder.channel in (ReminderChannel.push, ReminderChannel.both):
                if user.fcm_token:
                    _send_fcm_push(user.fcm_token, "Medication Reminder", msg)

            if reminder.channel in (ReminderChannel.whatsapp, ReminderChannel.both):
                if user.whatsapp_opted_in:
                    _send_whatsapp(user.phone, msg)


def _send_fcm_push(token: str, title: str, body: str):
    """Send FCM push notification."""
    import httpx
    try:
        httpx.post(
            "https://fcm.googleapis.com/fcm/send",
            json={"to": token, "notification": {"title": title, "body": body}},
            headers={"Authorization": f"key={settings.FCM_SERVER_KEY}"},
            timeout=5.0,
        )
    except Exception:
        pass  # Non-critical: notification delivery failure should not block


def _send_whatsapp(phone: str, message: str):
    """Send WhatsApp message via Meta Cloud API."""
    import httpx
    if not settings.WHATSAPP_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        return
    try:
        httpx.post(
            f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages",
            json={
                "messaging_product": "whatsapp",
                "to": phone.replace("+", ""),
                "type": "text",
                "text": {"body": message},
            },
            headers={"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"},
            timeout=5.0,
        )
    except Exception:
        pass
