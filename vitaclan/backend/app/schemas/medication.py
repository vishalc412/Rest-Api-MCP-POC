import uuid
from datetime import datetime, date, time
from pydantic import BaseModel
from app.models.medication import ReminderChannel


class MedicationCreate(BaseModel):
    name: str
    dosage: str | None = None
    frequency: str | None = None
    instructions: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    document_id: uuid.UUID | None = None


class MedicationUpdate(BaseModel):
    name: str | None = None
    dosage: str | None = None
    frequency: str | None = None
    instructions: str | None = None
    end_date: date | None = None
    is_active: bool | None = None


class MedicationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    dosage: str | None
    frequency: str | None
    instructions: str | None
    start_date: date | None
    end_date: date | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReminderCreate(BaseModel):
    medication_id: uuid.UUID
    schedule_time: time
    days_of_week: list[int] | None = None
    channel: ReminderChannel = ReminderChannel.push


class ReminderUpdate(BaseModel):
    schedule_time: time | None = None
    days_of_week: list[int] | None = None
    channel: ReminderChannel | None = None
    is_active: bool | None = None


class ReminderResponse(BaseModel):
    id: uuid.UUID
    medication_id: uuid.UUID
    schedule_time: time
    days_of_week: list[int] | None
    channel: ReminderChannel
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
