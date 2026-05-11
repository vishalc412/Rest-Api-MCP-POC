import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.medication import Medication, MedicationReminder
from app.schemas.medication import (
    MedicationCreate, MedicationUpdate, MedicationResponse,
    ReminderCreate, ReminderUpdate, ReminderResponse,
)

router = APIRouter(prefix="/medications", tags=["medications"])


@router.get("/", response_model=list[MedicationResponse])
async def list_medications(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Medication).where(Medication.user_id == current_user.id)
    if active_only:
        query = query.where(Medication.is_active == True)
    result = await db.execute(query.order_by(Medication.created_at.desc()))
    return result.scalars().all()


@router.post("/", response_model=MedicationResponse, status_code=201)
async def create_medication(
    body: MedicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    med = Medication(user_id=current_user.id, **body.model_dump())
    db.add(med)
    await db.commit()
    await db.refresh(med)
    return med


@router.put("/{med_id}", response_model=MedicationResponse)
async def update_medication(
    med_id: uuid.UUID,
    body: MedicationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    med = await _get_medication(db, med_id, current_user.id)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(med, field, value)
    await db.commit()
    await db.refresh(med)
    return med


@router.delete("/{med_id}", status_code=204)
async def delete_medication(
    med_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    med = await _get_medication(db, med_id, current_user.id)
    await db.delete(med)
    await db.commit()


# --- Reminders ---

@router.get("/reminders", response_model=list[ReminderResponse])
async def list_reminders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MedicationReminder)
        .join(Medication, MedicationReminder.medication_id == Medication.id)
        .where(Medication.user_id == current_user.id)
        .order_by(MedicationReminder.schedule_time)
    )
    return result.scalars().all()


@router.post("/reminders", response_model=ReminderResponse, status_code=201)
async def create_reminder(
    body: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_medication(db, body.medication_id, current_user.id)
    reminder = MedicationReminder(**body.model_dump())
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder


@router.put("/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: uuid.UUID,
    body: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    reminder = await _get_reminder(db, reminder_id, current_user.id)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(reminder, field, value)
    await db.commit()
    await db.refresh(reminder)
    return reminder


async def _get_medication(db: AsyncSession, med_id: uuid.UUID, user_id: uuid.UUID) -> Medication:
    result = await db.execute(
        select(Medication).where(Medication.id == med_id, Medication.user_id == user_id)
    )
    med = result.scalar_one_or_none()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    return med


async def _get_reminder(db: AsyncSession, reminder_id: uuid.UUID, user_id: uuid.UUID) -> MedicationReminder:
    result = await db.execute(
        select(MedicationReminder)
        .join(Medication, MedicationReminder.medication_id == Medication.id)
        .where(MedicationReminder.id == reminder_id, Medication.user_id == user_id)
    )
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder
