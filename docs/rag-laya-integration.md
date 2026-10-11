# RAG + Laya integration — review and operations

## What changed
- The existing React + FastAPI + MySQL application remains intact.
- Real document OCR and conservative structured extraction replace default mock examples. No claim is made that extracted records have been clinically verified.
- Human confirmation is required before extraction enters the Copilot's verified record retrieval set.
- New /api/copilot/ask is authenticated and strictly scoped to the current patient; answers carry document citations.
- Optional Laya decision routing is explicitly opt-in; its outputs never determine clinical correctness.
- Frontend includes a Copilot screen linked from the existing navigation.

## Local startup
Start MySQL with docker compose up -d mysql, install backend/requirements.txt, copy backend/.env.example to backend/.env, run uvicorn app.main:app --reload from backend, then run npm install and npm run dev from frontend.
Image OCR and scanned PDFs require installing the Tesseract executable independently.
Install Laya only when hardware and model availability are confirmed, and use LAYA_ENABLED=true only after a real inference smoke test.

## Tests
From backend, install pytest and run python -m pytest -q tests/test_real_ai.py.
These are small unit-level tests. The code has **not** yet passed end-to-end MySQL, browser, cloud deployment, Laya, OCR-across-real-scans, or clinical validation tests. Test outputs must be checked before merge.

## Mandatory pre-production work
1. Replace dev JWT secrets, harden password reset and authentication, rate limit endpoints, audit activity, restrict file storage, and encrypt sensitive data.
2. Replace FastAPI BackgroundTasks for heavyweight OCR with a durable work queue, idempotency keys and bounded worker concurrency.
3. Add MIME scanning, malware scanning, image decompression checks and strong upload resource quotas.
4. Benchmark OCR/extraction on diverse real-world scans, handwritten prescriptions, and bilingual texts; display field-level provenance and confidence.
5. Run an independently reviewed clinical safety evaluation. Laya's pretrained router is NOT a validated medical evidence classifier.
6. Use real FHIR/ABDM validation and verified health data consent flows; mock ABHA does not imply real ABHA connectivity.
7. Implement model gateway privacy checks; do not send personal health information to remote models without legally valid consent and protection.
8. Add DB migrations, comprehensive CI, accessibility checks, backups and disaster recovery exercises.

**Privacy note:** Never upload real patient records to a public demo or demo credentials.
