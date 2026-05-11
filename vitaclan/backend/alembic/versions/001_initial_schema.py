"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, INTEGER, TEXT

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector and uuid
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Enums
    op.execute("CREATE TYPE family_member_role AS ENUM ('owner', 'admin', 'member', 'view-only')")
    op.execute("CREATE TYPE document_type AS ENUM ('prescription', 'lab_report', 'bill', 'doctor_note', 'other')")
    op.execute("CREATE TYPE ocr_status AS ENUM ('pending', 'processing', 'completed', 'failed')")
    op.execute("CREATE TYPE reminder_channel AS ENUM ('push', 'whatsapp', 'both')")
    op.execute("CREATE TYPE expense_category AS ENUM ('doctor_fee', 'lab_test', 'medicine', 'other')")

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("phone", sa.String(15), unique=True, nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("abha_id", sa.String(50)),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("language", sa.String(10), server_default="en"),
        sa.Column("fcm_token", sa.String(500)),
        sa.Column("whatsapp_opted_in", sa.Boolean, server_default="false"),
        sa.Column("consent_given_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "families",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("owner_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "family_members",
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id"), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("role", sa.Enum("owner", "admin", "member", "view-only", name="family_member_role"), nullable=False),
        sa.Column("privacy", JSONB, server_default="{}"),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "health_profiles",
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("blood_group", sa.String(5)),
        sa.Column("allergies", ARRAY(TEXT)),
        sa.Column("conditions", ARRAY(TEXT)),
        sa.Column("emergency_summary", JSONB),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "medical_documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("family_id", UUID(as_uuid=True), sa.ForeignKey("families.id")),
        sa.Column("type", sa.Enum("prescription", "lab_report", "bill", "doctor_note", "other", name="document_type"), nullable=False),
        sa.Column("raw_image_url", sa.Text, nullable=False),
        sa.Column("ocr_text", sa.Text),
        sa.Column("structured_data", JSONB),
        sa.Column("ai_summary", sa.Text),
        sa.Column("ai_confidence", sa.Float),
        sa.Column("ai_sources", JSONB),
        sa.Column("ocr_status", sa.Enum("pending", "processing", "completed", "failed", name="ocr_status"), server_default="pending"),
        sa.Column("language", sa.String(10), server_default="en"),
        sa.Column("document_date", sa.Date),
        sa.Column("doctor_name", sa.String(255)),
        sa.Column("hospital_name", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("retention_until", sa.Date),
    )
    op.create_index("ix_medical_documents_user_id", "medical_documents", ["user_id"])
    op.create_index("ix_medical_documents_created_at", "medical_documents", ["created_at"])

    op.create_table(
        "medications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("document_id", UUID(as_uuid=True), sa.ForeignKey("medical_documents.id")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("dosage", sa.String(100)),
        sa.Column("frequency", sa.String(100)),
        sa.Column("instructions", sa.Text),
        sa.Column("start_date", sa.Date),
        sa.Column("end_date", sa.Date),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "medication_reminders",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("medication_id", UUID(as_uuid=True), sa.ForeignKey("medications.id"), nullable=False),
        sa.Column("schedule_time", sa.Time, nullable=False),
        sa.Column("days_of_week", ARRAY(INTEGER)),
        sa.Column("channel", sa.Enum("push", "whatsapp", "both", name="reminder_channel"), server_default="push"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "health_expenses",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("document_id", UUID(as_uuid=True), sa.ForeignKey("medical_documents.id")),
        sa.Column("amount", sa.Numeric(10, 2)),
        sa.Column("category", sa.Enum("doctor_fee", "lab_test", "medicine", "other", name="expense_category"), server_default="other"),
        sa.Column("expense_date", sa.Date),
        sa.Column("vendor_name", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "voice_notes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("transcription", sa.Text),
        sa.Column("audio_url", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource", sa.String(100)),
        sa.Column("resource_id", UUID(as_uuid=True)),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "otp_codes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("phone", sa.String(15), nullable=False),
        sa.Column("code", sa.String(6), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_otp_codes_phone", "otp_codes", ["phone"])


def downgrade() -> None:
    op.drop_table("otp_codes")
    op.drop_table("audit_log")
    op.drop_table("voice_notes")
    op.drop_table("health_expenses")
    op.drop_table("medication_reminders")
    op.drop_table("medications")
    op.drop_table("medical_documents")
    op.drop_table("health_profiles")
    op.drop_table("family_members")
    op.drop_table("families")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS expense_category")
    op.execute("DROP TYPE IF EXISTS reminder_channel")
    op.execute("DROP TYPE IF EXISTS ocr_status")
    op.execute("DROP TYPE IF EXISTS document_type")
    op.execute("DROP TYPE IF EXISTS family_member_role")
