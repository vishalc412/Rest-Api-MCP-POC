# VitaClan — Vital records for your clan

**Unified Family Health Intelligence Platform** — Transform scattered medical papers into a secure, intelligent, and shareable health ecosystem.

## What's Inside

- **Mobile app** (React Native + Expo) — scan documents, view AI summaries, voice queries, family hub
- **Backend API** (FastAPI + PostgreSQL + Redis) — DPDP-compliant, deployable to AWS ap-south-1
- **AI/OCR Pipeline** (Ollama LLaVA + Llama 3.3 + ChromaDB RAG) — self-hosted, India-data-resident
- **Worker** (Celery) — async OCR processing, medication reminders
- **Storage** (MinIO local / S3 Mumbai prod) — encrypted document storage

## Architecture
Mobile (RN + Expo)
↓ HTTPS + JWT
FastAPI API ──→ Celery Workers ──→ Ollama (LLaVA + Llama 3.3) ──→ ChromaDB (RAG)
↓                                              ↓
PostgreSQL (PHI) + MinIO/S3 (encrypted docs)
↑
Redis (cache, queues, sessions)

## Quick Start (Local Dev)

### Prerequisites
- Docker Desktop 4.20+ (with 16GB RAM minimum allocated)
- Node 20+ and npm
- 60GB free disk space for Ollama models

### 1. Boot the backend stack
```bash
cd vitaclan/infra
docker compose up -d

# Wait ~30 seconds for services to be healthy, then check:
docker compose ps
```

### 2. Pull Ollama models (~40GB, one-time)

```bash
docker exec -it vitaclan-ollama-1 ollama pull llama3.3:70b
docker exec -it vitaclan-ollama-1 ollama pull llava:13b
docker exec -it vitaclan-ollama-1 ollama pull nomic-embed-text
```

For low-RAM machines, swap `llama3.3:70b` → `llama3.2:3b` in `.env`.

### 3. Run database migrations

```bash
docker exec vitaclan-api-1 alembic upgrade head
```

### 4. Seed RAG knowledge base

```bash
docker exec vitaclan-api-1 python -m rag_ingestion.ingest_indian_medicines
docker exec vitaclan-api-1 python -m rag_ingestion.ingest_openfda
```

### 5. Verify backend
Open http://localhost:8000/docs — FastAPI Swagger UI should load.

Health check:
```bash
curl http://localhost:8000/health
```

### 6. Run mobile app

```bash
cd ../mobile
npm install
npx expo start
```

Scan the QR code with Expo Go app on your phone, OR press `i` for iOS sim / `a` for Android emulator.

## Project Structure

```
vitaclan/
├── backend/              # FastAPI + Celery
│   ├── app/
│   │   ├── api/v1/       # Route handlers
│   │   ├── core/         # Config, DB, security, deps
│   │   ├── models/       # SQLAlchemy ORM
│   │   ├── schemas/      # Pydantic models
│   │   ├── services/
│   │   │   ├── ocr/      # OCR cascade pipeline
│   │   │   ├── ai/       # LLM interpreter + voice query
│   │   │   └── storage/  # S3/MinIO abstraction
│   │   ├── worker/       # Celery tasks
│   │   └── main.py
│   ├── alembic/          # DB migrations
│   ├── rag_ingestion/    # ChromaDB seed scripts
│   └── Dockerfile
├── mobile/               # React Native + Expo
│   ├── src/
│   │   ├── screens/      # Timeline, Scan, Family, Voice, etc.
│   │   ├── stores/       # Zustand auth store
│   │   ├── api/          # React Query + Axios client
│   │   └── navigation/
│   └── App.tsx
└── infra/
    └── docker-compose.yml
```

## Decision Log

See `plans/grill-me-with-question-glistening-wall.md` for the full architecture decision log (26 design choices grilled across 8 branches).

Key decisions:
- **India-first** (DPDP Act 2023, no HIPAA)
- **Wellness app** (no clinical claims, no SaMD/FDA path)
- **Volume-first growth** with aggressive AI rate-limiting on free tier
- **Self-hosted Ollama** for cost control (Llama 3.3 70B + LLaVA 1.6)
- **Mobile + WhatsApp-first** distribution
- **ML Kit on-device OCR** with LLaVA + Cloud Vision fallback

## DPDP Compliance Checklist

- [x] Explicit consent at signup, stored with timestamp
- [x] Audit log for every PHI access
- [x] Right-to-erasure: `DELETE /users/me` cascades all data
- [x] Data localization: All services in ap-south-1 (Mumbai)
- [x] 7-year retention default, user-configurable
- [x] Purpose limitation: no PHI used for ads or ML training
- [ ] Privacy policy in English + Hindi (post-MVP)

## AI Safety Posture

Every AI-generated response includes:
1. Mandatory disclaimer: "This is not medical advice."
2. Source citation (OpenFDA, curated Indian Pharmacopoeia, ICMR/WHO)
3. Confidence score (0.0–1.0)
4. No diagnosis or prescription language ever

## Production Deployment

See `plans/grill-me-with-question-glistening-wall.md` → "Infrastructure" section for AWS ECS Fargate setup. Key components:
- ECS Fargate (API + Celery)
- EC2 g4dn.* (Ollama GPU)
- RDS PostgreSQL
- ElastiCache Redis
- S3 (ap-south-1, AES-256, versioned)

## License

Proprietary. © 2026 VitaClan.
