"""
S3/MinIO storage abstraction — same API for local dev (MinIO) and prod (AWS S3).
"""
import uuid
import boto3
from botocore.config import Config
from app.core.config import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT if settings.S3_ENDPOINT != "https://s3.amazonaws.com" else None,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version="s3v4"),
        )
        # Ensure bucket exists (MinIO dev)
        try:
            _client.head_bucket(Bucket=settings.S3_BUCKET)
        except Exception:
            _client.create_bucket(Bucket=settings.S3_BUCKET)
    return _client


async def upload_document(content: bytes, user_id: str, filename: str) -> str:
    """Upload encrypted document to S3/MinIO. Returns S3 key."""
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
    key = f"documents/{user_id}/{uuid.uuid4()}.{ext}"

    client = _get_client()
    client.put_object(
        Bucket=settings.S3_BUCKET,
        Key=key,
        Body=content,
        ContentType=f"image/{ext}",
        ServerSideEncryption="AES256",
    )
    return key


async def get_presigned_url(key: str, expires_in: int = 3600) -> str:
    """Generate a time-limited presigned URL for secure document access."""
    client = _get_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": key},
        ExpiresIn=expires_in,
    )


async def download_document(key: str) -> bytes:
    """Download document bytes for OCR processing."""
    client = _get_client()
    response = client.get_object(Bucket=settings.S3_BUCKET, Key=key)
    return response["Body"].read()


async def delete_document(key: str) -> None:
    """Permanent deletion — called on DPDP right-to-erasure."""
    client = _get_client()
    client.delete_object(Bucket=settings.S3_BUCKET, Key=key)
