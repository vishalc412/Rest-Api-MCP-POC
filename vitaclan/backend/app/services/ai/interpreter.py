"""
AI Medical Interpreter — RAG-grounded explanation of medical documents.
Grounds every response in ChromaDB (OpenFDA + medical knowledge base).
Never diagnoses. Always disclaims.
"""
import chromadb
from langchain_ollama import OllamaLLM
from langchain.schema import HumanMessage, SystemMessage
from app.core.config import settings

SYSTEM_PROMPT = """You are VitaClan's health information assistant. You help Indian families understand their medical documents in simple language.

STRICT RULES:
1. Explain medical terms in simple {language} language
2. NEVER diagnose any condition
3. NEVER recommend or change medications
4. ALWAYS cite which source you used (OpenFDA, medical literature, etc.)
5. If you are not sure about something, say "Please ask your doctor about this"
6. Keep explanations brief and friendly

You are NOT a doctor. You provide health information, not medical advice."""


def get_chroma_client():
    return chromadb.HttpClient(
        host=settings.CHROMA_HOST,
        port=settings.CHROMA_PORT,
    )


def get_llm():
    return OllamaLLM(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_LLM_MODEL,
        temperature=0.1,  # Low temp for medical accuracy
    )


async def interpret_medical_document(
    structured_data: dict,
    language: str = "en",
) -> tuple[str, float, list[str]]:
    """
    Generate AI explanation for a medical document.
    Returns (summary, confidence, sources)
    """
    # Retrieve relevant context from RAG
    medicine_names = [m.get("name", "") for m in structured_data.get("medicines", [])]
    test_names = [t.get("name", "") for t in structured_data.get("tests", [])]
    rag_context, sources = _retrieve_rag_context(medicine_names + test_names)

    doc_summary = _format_document_for_prompt(structured_data)
    lang_name = "Hindi" if language == "hi" else "English"

    prompt = f"""Medical document data:
{doc_summary}

Reference information from trusted sources:
{rag_context}

Please explain this medical document to a patient in simple {lang_name}.
Cover: what medicines are prescribed (purpose, how to take), what tests show (what the results mean), and any important instructions.
Cite sources where applicable."""

    llm = get_llm()
    system = SYSTEM_PROMPT.format(language=lang_name)

    try:
        response = llm.invoke(f"{system}\n\n{prompt}")
        confidence = 0.80 if rag_context else 0.60
        return str(response), confidence, sources
    except Exception as e:
        return f"Could not generate summary: {str(e)}", 0.0, []


def _retrieve_rag_context(terms: list[str]) -> tuple[str, list[str]]:
    """Query ChromaDB for relevant medical knowledge."""
    if not terms:
        return "", []

    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection("medical_knowledge")

        results = collection.query(
            query_texts=terms[:5],  # Limit to avoid token overflow
            n_results=3,
        )

        chunks = []
        sources = []
        for docs, metas in zip(results["documents"], results["metadatas"]):
            for doc, meta in zip(docs, metas):
                chunks.append(doc[:500])  # Truncate each chunk
                if meta.get("source"):
                    sources.append(meta["source"])

        return "\n\n".join(chunks), list(set(sources))
    except Exception:
        return "", []


def _format_document_for_prompt(data: dict) -> str:
    parts = []
    if data.get("medicines"):
        parts.append("Medicines prescribed:")
        for m in data["medicines"]:
            parts.append(f"  - {m.get('name', 'Unknown')}: {m.get('dosage', '')} {m.get('frequency', '')}")
    if data.get("tests"):
        parts.append("Test results:")
        for t in data["tests"]:
            parts.append(f"  - {t.get('name', 'Unknown')}: {t.get('result', '')} {t.get('unit', '')} (normal: {t.get('normal_range', 'N/A')})")
    if data.get("doctor"):
        parts.append(f"Doctor: {data['doctor']}")
    if data.get("hospital"):
        parts.append(f"Hospital: {data['hospital']}")
    return "\n".join(parts) if parts else "No structured data extracted"
