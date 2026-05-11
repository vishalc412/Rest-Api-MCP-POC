"""
Ingest OpenFDA drug data into ChromaDB for AI Medical Interpreter RAG.

OpenFDA endpoint: https://api.fda.gov/drug/label.json
Free, no auth required (rate limit 240 requests/min, 1000/day without API key).

Run after `docker compose up`:
    docker exec vitaclan-api python -m rag_ingestion.ingest_openfda
"""
import asyncio
import json
import logging
import httpx
import chromadb
from typing import Iterable
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENFDA_BASE = "https://api.fda.gov/drug/label.json"
PAGE_SIZE = 100
MAX_PAGES = 50  # 5000 drug labels for MVP — extend post-launch


async def fetch_openfda_page(skip: int) -> list[dict]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            OPENFDA_BASE,
            params={"limit": PAGE_SIZE, "skip": skip},
        )
        response.raise_for_status()
        return response.json().get("results", [])


def label_to_document(label: dict) -> tuple[str, dict] | None:
    """Convert OpenFDA drug label to a RAG-friendly text chunk + metadata."""
    openfda = label.get("openfda", {})
    brand_names = openfda.get("brand_name", [])
    generic_names = openfda.get("generic_name", [])
    name = (brand_names + generic_names)[:1]
    if not name:
        return None

    parts = [f"Drug: {name[0]}"]
    if generic_names:
        parts.append(f"Generic name: {', '.join(generic_names)}")

    sections = {
        "Indications and Usage": label.get("indications_and_usage"),
        "Dosage and Administration": label.get("dosage_and_administration"),
        "Warnings": label.get("warnings"),
        "Adverse Reactions": label.get("adverse_reactions"),
        "Drug Interactions": label.get("drug_interactions"),
        "Pregnancy": label.get("pregnancy"),
    }
    for title, text in sections.items():
        if text:
            joined = " ".join(text) if isinstance(text, list) else str(text)
            parts.append(f"\n{title}: {joined[:1500]}")  # Truncate verbose sections

    return "\n".join(parts), {
        "source": "OpenFDA",
        "drug_name": name[0],
        "generic_names": ",".join(generic_names),
    }


def embed_via_ollama(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using Ollama nomic-embed-text (free, local)."""
    import httpx
    embeddings = []
    with httpx.Client(timeout=60.0) as client:
        for text in texts:
            r = client.post(
                f"{settings.OLLAMA_BASE_URL}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
            )
            r.raise_for_status()
            embeddings.append(r.json()["embedding"])
    return embeddings


async def ingest():
    logger.info("Connecting to ChromaDB at %s:%s", settings.CHROMA_HOST, settings.CHROMA_PORT)
    client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    collection = client.get_or_create_collection(
        "medical_knowledge",
        metadata={"hnsw:space": "cosine"},
    )

    logger.info("Starting OpenFDA ingestion: up to %d pages of %d labels each", MAX_PAGES, PAGE_SIZE)

    for page in range(MAX_PAGES):
        skip = page * PAGE_SIZE
        try:
            labels = await fetch_openfda_page(skip)
        except Exception as e:
            logger.warning("Page %d failed: %s", page, e)
            continue

        if not labels:
            break

        docs, metadatas, ids = [], [], []
        for i, label in enumerate(labels):
            converted = label_to_document(label)
            if not converted:
                continue
            text, meta = converted
            docs.append(text)
            metadatas.append(meta)
            ids.append(f"openfda_{skip + i}")

        if not docs:
            continue

        embeddings = embed_via_ollama(docs)
        collection.upsert(documents=docs, metadatas=metadatas, ids=ids, embeddings=embeddings)
        logger.info("Page %d: ingested %d drug labels", page, len(docs))

    logger.info("Ingestion complete. Total in collection: %d", collection.count())


if __name__ == "__main__":
    asyncio.run(ingest())
