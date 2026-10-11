# MedCare — AI Personal Health Copilot

Web app for the Altrix Labs challenge: upload medical records, extract structured data (mock AI for now), show plain-language summaries (English/Hindi), unified timeline, medications, lab trends, and ABDM/FHIR-ready export with mock ABHA linking.

**Stack:** React + Tailwind · FastAPI · MySQL

## Quick start

### 1. Start MySQL

```bash
docker compose up -d mysql
```

### 2. Backend

```bash
cd backend
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # or cp .env.example .env

uvicorn app.main:app --reload --port 8000
```

In another terminal (with venv active):

```bash
cd backend
python seed.py
```

Demo login: **demo@medcare.app** / **demo1234**

API docs: http://127.0.0.1:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Features

- Upload prescriptions, lab reports, discharge summaries, diagnostic reports
- Mock OCR + extraction + EN/HI summaries (pluggable for the AI team)
- Human review / confirm before data enters the health profile
- Timeline, medications, lab trend charts with reference bands
- Mock ABHA link (OTP `123456`) + sample FHIR import + FHIR Bundle export
- Persistent medical disclaimer

## Project layout

```
MedCare/
  backend/          FastAPI app, AI providers, FHIR mapper
  frontend/         Vite React + Tailwind SPA
  docs/             Architecture + AI integration contract
  docker-compose.yml
```

## AI team handoff

See [docs/ai-integration.md](docs/ai-integration.md). Set `AI_PROVIDER=team` after implementing the provider classes.

## Design

Inspo MCP is configured for Cursor (`npx -y inspo-mcp install`). UI tokens follow a calm healthcare palette (teal brand, Fraunces + Inter). Restart Cursor to use Inspo tools for further design refinement.
