"""
Seed ChromaDB with curated Indian medicine knowledge (CDSCO common drugs, AYUSH context).
OpenFDA covers US drugs — supplement with India-specific data.

Run: docker exec vitaclan-api python -m rag_ingestion.ingest_indian_medicines
"""
import asyncio
import logging
import chromadb
import httpx
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Curated Indian top-selling medicines (placeholder — replace with full dataset post-MVP)
INDIAN_MEDICINES = [
    {
        "name": "Crocin",
        "generic": "Paracetamol",
        "uses": "Fever, mild to moderate pain (headache, body ache, toothache, menstrual cramps).",
        "dosage": "Adults: 500-1000 mg every 4-6 hours, max 4 g/day. Children: 10-15 mg/kg per dose.",
        "warnings": "Do not exceed 4 g per day. Avoid alcohol. Liver damage risk in overdose.",
        "side_effects": "Rare at therapeutic doses. May cause skin rash, nausea.",
    },
    {
        "name": "Combiflam",
        "generic": "Ibuprofen + Paracetamol",
        "uses": "Pain relief, fever, inflammation. Useful for joint pain, sprains.",
        "dosage": "1 tablet every 8 hours after food. Maximum 3 tablets per day.",
        "warnings": "Avoid in pregnancy (3rd trimester), kidney issues, peptic ulcer, asthma.",
        "side_effects": "Stomach upset, nausea, dizziness. Long-term use may cause GI bleeding.",
    },
    {
        "name": "Dolo 650",
        "generic": "Paracetamol 650mg",
        "uses": "Fever and mild to moderate pain. Widely used for viral fever.",
        "dosage": "1 tablet every 4-6 hours, max 4 tablets in 24 hours.",
        "warnings": "Avoid alcohol. Check for paracetamol in other medicines to avoid overdose.",
        "side_effects": "Generally safe. Rare allergic reactions.",
    },
    {
        "name": "Augmentin",
        "generic": "Amoxicillin + Clavulanic Acid",
        "uses": "Bacterial infections — respiratory tract, urinary tract, skin, dental.",
        "dosage": "625 mg every 12 hours for 5-7 days. Take with food.",
        "warnings": "Complete the full course even if symptoms improve. Penicillin allergy = contraindicated.",
        "side_effects": "Diarrhea, nausea, vomiting, candidiasis.",
    },
    {
        "name": "Pantop",
        "generic": "Pantoprazole",
        "uses": "Acidity, GERD (acid reflux), peptic ulcers, Zollinger-Ellison syndrome.",
        "dosage": "40 mg once daily before breakfast, for 4-8 weeks typically.",
        "warnings": "Long-term use may cause B12 deficiency, bone fractures, kidney issues.",
        "side_effects": "Headache, diarrhea, abdominal pain.",
    },
    {
        "name": "Metformin",
        "generic": "Metformin Hydrochloride",
        "uses": "Type 2 diabetes — first-line treatment. Also used in PCOS.",
        "dosage": "500-1000 mg twice daily with meals. Max 2000-2500 mg/day.",
        "warnings": "Monitor kidney function. Stop before contrast imaging. Avoid in severe liver/kidney disease.",
        "side_effects": "GI upset, metallic taste, B12 deficiency (long-term).",
    },
    {
        "name": "Telma",
        "generic": "Telmisartan",
        "uses": "High blood pressure (hypertension), cardiovascular protection.",
        "dosage": "40-80 mg once daily.",
        "warnings": "Avoid in pregnancy. Monitor potassium, kidney function.",
        "side_effects": "Dizziness, back pain, sinusitis.",
    },
    {
        "name": "Atorva",
        "generic": "Atorvastatin",
        "uses": "Lowers LDL cholesterol, reduces heart attack and stroke risk.",
        "dosage": "10-80 mg once daily, usually at night.",
        "warnings": "Monitor liver enzymes. Report muscle pain immediately (rhabdomyolysis risk).",
        "side_effects": "Muscle pain, headache, GI upset.",
    },
]

LAB_TESTS = [
    {
        "name": "CBC (Complete Blood Count)",
        "explanation": "Measures red blood cells, white blood cells, platelets, hemoglobin. Used to detect anemia, infections, blood disorders.",
        "normal_ranges": "Hemoglobin: Men 13.5-17.5 g/dL, Women 12.0-15.5 g/dL. WBC: 4000-11000/μL. Platelets: 150,000-450,000/μL.",
    },
    {
        "name": "HbA1c (Glycated Hemoglobin)",
        "explanation": "Shows average blood sugar over 2-3 months. Used to diagnose and monitor diabetes.",
        "normal_ranges": "Normal: <5.7%. Prediabetes: 5.7-6.4%. Diabetes: ≥6.5%.",
    },
    {
        "name": "Lipid Profile",
        "explanation": "Cholesterol panel — measures total cholesterol, LDL (bad), HDL (good), triglycerides.",
        "normal_ranges": "Total cholesterol: <200 mg/dL. LDL: <100 mg/dL. HDL: >40 (men), >50 (women). Triglycerides: <150 mg/dL.",
    },
    {
        "name": "TSH (Thyroid Stimulating Hormone)",
        "explanation": "Screens for thyroid dysfunction. High TSH = hypothyroid. Low TSH = hyperthyroid.",
        "normal_ranges": "0.4-4.0 mIU/L (varies by lab and pregnancy status).",
    },
    {
        "name": "Vitamin D (25-hydroxy)",
        "explanation": "Vitamin D deficiency is widespread in India. Affects bone health, immunity, mood.",
        "normal_ranges": "Sufficient: 30-100 ng/mL. Insufficient: 20-29. Deficient: <20.",
    },
]


def embed_text(text: str) -> list[float]:
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            f"{settings.OLLAMA_BASE_URL}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
        )
        r.raise_for_status()
        return r.json()["embedding"]


async def ingest():
    client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
    collection = client.get_or_create_collection("medical_knowledge")

    docs, metadatas, ids, embeddings = [], [], [], []

    for i, med in enumerate(INDIAN_MEDICINES):
        text = (
            f"Medicine: {med['name']} (generic: {med['generic']})\n"
            f"Uses: {med['uses']}\n"
            f"Dosage: {med['dosage']}\n"
            f"Warnings: {med['warnings']}\n"
            f"Side effects: {med['side_effects']}"
        )
        docs.append(text)
        metadatas.append({"source": "Indian Pharmacopoeia (curated)", "drug_name": med["name"]})
        ids.append(f"in_med_{i}")
        embeddings.append(embed_text(text))

    for i, test in enumerate(LAB_TESTS):
        text = (
            f"Lab Test: {test['name']}\n"
            f"Explanation: {test['explanation']}\n"
            f"Normal ranges: {test['normal_ranges']}"
        )
        docs.append(text)
        metadatas.append({"source": "WHO + ICMR guidelines", "test_name": test["name"]})
        ids.append(f"in_test_{i}")
        embeddings.append(embed_text(text))

    collection.upsert(documents=docs, metadatas=metadatas, ids=ids, embeddings=embeddings)
    logger.info("Ingested %d Indian medicine + test entries. Total in collection: %d",
                len(docs), collection.count())


if __name__ == "__main__":
    asyncio.run(ingest())
