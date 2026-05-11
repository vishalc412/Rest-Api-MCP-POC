"""
OCR pipeline: confidence-based cascade from cheap to expensive.
ML Kit result (from mobile) → LLaVA via Ollama → Google Cloud Vision fallback
"""
import base64
import json
import httpx
from app.core.config import settings

EXTRACTION_PROMPT = """You are a medical document parser. Extract structured data from this medical document image.

Return ONLY valid JSON with this exact structure:
{
  "medicines": [{"name": "string", "dosage": "string", "frequency": "string", "instructions": "string"}],
  "tests": [{"name": "string", "result": "string", "unit": "string", "normal_range": "string"}],
  "cost": {"total": 0.0, "breakdown": [{"item": "string", "amount": 0.0}]},
  "doctor": "string or null",
  "hospital": "string or null",
  "date": "YYYY-MM-DD or null",
  "raw_text": "full extracted text"
}

If a field is not present, use null or empty array. Do not include commentary outside the JSON."""


async def extract_with_llava(image_bytes: bytes) -> tuple[dict, float]:
    """Send image to LLaVA via Ollama, return (structured_data, confidence)."""
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_VISION_MODEL,
                "prompt": EXTRACTION_PROMPT,
                "images": [image_b64],
                "stream": False,
                "format": "json",
            },
        )
        response.raise_for_status()
        result = response.json()

    raw_response = result.get("response", "{}")
    try:
        structured = json.loads(raw_response)
        # Basic confidence heuristic: more fields filled = higher confidence
        filled = sum(1 for v in structured.values() if v)
        confidence = min(0.95, filled / 7 * 0.8 + 0.2)
        return structured, confidence
    except json.JSONDecodeError:
        return {"raw_text": raw_response}, 0.3


async def extract_with_cloud_vision(image_bytes: bytes) -> tuple[dict, float]:
    """Google Cloud Vision OCR fallback for low-confidence results."""
    try:
        from google.cloud import vision  # type: ignore
        import io

        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_bytes)
        response = client.text_detection(image=image)

        if response.error.message:
            return {"raw_text": ""}, 0.0

        texts = response.text_annotations
        if not texts:
            return {"raw_text": ""}, 0.0

        full_text = texts[0].description
        return {"raw_text": full_text}, 0.7  # Cloud Vision gives text; LLM still needed for structure
    except Exception:
        return {"raw_text": ""}, 0.0


async def structure_ocr_text(ocr_text: str, language: str = "en") -> tuple[dict, float]:
    """Run Llama 3.3 70B to structure raw OCR text into typed fields."""
    prompt = f"""Extract structured medical data from this OCR text. Language hint: {language}.

OCR Text:
{ocr_text}

{EXTRACTION_PROMPT}"""

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
        )
        response.raise_for_status()
        result = response.json()

    raw = result.get("response", "{}")
    try:
        structured = json.loads(raw)
        filled = sum(1 for v in structured.values() if v)
        confidence = min(0.92, filled / 7 * 0.75 + 0.25)
        return structured, confidence
    except json.JSONDecodeError:
        return {"raw_text": ocr_text}, 0.2


async def run_ocr_pipeline(
    image_bytes: bytes,
    ml_kit_text: str | None = None,
    ml_kit_confidence: float = 0.0,
    language: str = "en",
) -> tuple[dict, float, str]:
    """
    Full OCR pipeline with confidence cascade.
    Returns (structured_data, confidence, method_used)
    """
    # If ML Kit gave high-confidence result, structure it directly
    if ml_kit_text and ml_kit_confidence >= 0.70:
        structured, confidence = await structure_ocr_text(ml_kit_text, language)
        if confidence >= 0.65:
            return structured, confidence, "ml_kit+llm"

    # LLaVA vision model on full image
    structured, confidence = await extract_with_llava(image_bytes)
    if confidence >= 0.65:
        return structured, confidence, "llava"

    # Cloud Vision fallback
    cloud_data, cloud_conf = await extract_with_cloud_vision(image_bytes)
    if cloud_data.get("raw_text"):
        structured, confidence = await structure_ocr_text(cloud_data["raw_text"], language)
        return structured, confidence, "cloud_vision+llm"

    return structured, confidence, "llava_low_conf"
