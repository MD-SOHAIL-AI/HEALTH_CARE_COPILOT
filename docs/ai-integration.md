# AI Integration Contract

The web app calls three Python protocols. The Round‑1 build ships **mock** providers. The AI team can replace them without changing routes, schema, or UI.

## Switch provider

In `backend/.env`:

```env
AI_PROVIDER=mock
# AI_PROVIDER=team   # after you register Team* classes in registry.py
```

## Protocols

File: `backend/app/services/ai/base.py`

### OCRProvider

```python
def extract_text(self, file_path: str, mime: str) -> OCRResult:
    # OCRResult(text, language, confidence)
```

### ExtractionProvider

```python
def extract(self, text: str, doc_type: DocumentType) -> ExtractionResult:
    # medications, observations, conditions, encounters, record_date, source_facility
```

### SummaryProvider

```python
def summarize(self, extraction: ExtractionResult, lang: str) -> SummaryResult:
    # plain_text, abnormal_explanations[], language, disclaimer
```

`lang` is `en` or `hi` (extendable).

## Sample ExtractionResult (JSON-shaped)

```json
{
  "medications": [
    {
      "name": "Metformin",
      "strength": "500 mg",
      "dosage": "1 tablet",
      "frequency": "twice daily",
      "route": "oral",
      "duration": "30 days",
      "confidence": 0.93
    }
  ],
  "observations": [
    {
      "test_name": "HbA1c",
      "value": 7.2,
      "unit": "%",
      "ref_low": 4.0,
      "ref_high": 5.6,
      "loinc_code": "4548-4",
      "confidence": 0.95
    }
  ],
  "conditions": [
    { "name": "Type 2 Diabetes Mellitus", "icd10_code": "E11", "confidence": 0.8 }
  ],
  "encounters": [],
  "record_date": "2025-10-20",
  "source_facility": "Dr. Sharma Clinic"
}
```

## How to plug in team models

1. Create `backend/app/services/ai/team.py` implementing the three protocols.
2. Update `backend/app/services/ai/registry.py` to return team classes when `AI_PROVIDER=team`.
3. Keep return types identical so the pipeline (`services/pipeline.py`) needs no changes.

## Pipeline order

1. OCR → store `ocr_text`, confidence, language  
2. Extraction → draft medications / observations / conditions / encounters  
3. Reference-range enrichment + H/L/N interpretation  
4. Summaries in EN and HI  
5. Status → `needs_review`  
6. User confirm → verified + timeline events  
