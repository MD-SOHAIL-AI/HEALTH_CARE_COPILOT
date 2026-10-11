"""Evidence-only extraction providers. Unrecognized facts remain unfilled, never fabricated."""
import io
import re
from datetime import date, datetime
from pathlib import Path

from app.models.entities import DocumentType
from app.services.ai.base import (
    OCRResult, ExtractionResult, ExtractedMedication, ExtractedObservation, SummaryResult,
)

LAB_ALIASES = {
    "hb": "Hemoglobin", "hgb": "Hemoglobin", "haemoglobin": "Hemoglobin",
    "hemoglobin": "Hemoglobin", "hba1c": "HbA1c",
    "fasting glucose": "Fasting Glucose", "fasting blood sugar": "Fasting Glucose",
    "fbs": "Fasting Glucose", "tsh": "TSH", "creatinine": "Creatinine",
    "total cholesterol": "Total Cholesterol", "ldl": "LDL Cholesterol",
    "ldl cholesterol": "LDL Cholesterol", "platelets": "Platelets",
}
LAB = re.compile(
    r"^\s*([A-Za-z][A-Za-z\s\d/-]{1,48}?)\s*[:\t ]+\s*(\d+(?:\.\d+)?)\s*"
    r"(%|g/dL|mg/dL|mmol/L|mIU/L|uIU/mL|ng/mL|IU/L|mg/L|pg/mL)?\s*"
    r"(?:\(?\s*(?:ref(?:erence)?(?:\s*range)?|normal|range)\s*[:=]?\s*)?"
    r"\(?\s*(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)\s*\)?\s*$",
    re.IGNORECASE,
)
RX = re.compile(
    r"^\s*(?:\d+[.)]\s*)?(?:Tab\.?|Tablet|Cap\.?|Capsule)\s+"
    r"([A-Za-z][A-Za-z0-9 -]{1,38}?)\s+"
    r"(\d+(?:\.\d+)?\s*(?:mg|mcg|g|ml|IU))\b"
    r"(?:\s*[-,:]\s*|\s+)(once daily|twice daily|three times daily|daily|"
    r"at night|morning and night|after food|before food|OD|BD|TID|1-0-1|1-0-0|0-0-1)\b",
    re.IGNORECASE,
)
DATE = re.compile(r"\b(?:date|collected|report date)\s*[:\-]\s*(\d{4}-\d{2}-\d{2}|\d{2}[/-]\d{2}[/-]\d{4})", re.I)


def parsed_date(text: str) -> date | None:
    match = DATE.search(text[:3000])
    if not match:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            parsed = datetime.strptime(match.group(1), fmt).date()
            return parsed if 1900 <= parsed.year <= date.today().year + 1 else None
        except ValueError:
            continue
    return None


class RealOCRProvider:
    def extract_text(self, file_path: str, mime: str) -> OCRResult:
        path = Path(file_path)
        content = path.read_bytes()
        if not content:
            raise ValueError("Empty document")
        if content.startswith(b"%PDF"):
            import fitz
            pdf = fitz.open(stream=content, filetype="pdf")
            try:
                if pdf.is_encrypted or not 1 <= len(pdf) <= 20:
                    raise ValueError("Encrypted or longer-than-20-page PDFs cannot be processed")
                texts = []
                scanned = False
                for page in pdf:
                    txt = page.get_text(sort=True)
                    if len(txt.strip()) < 30:
                        from PIL import Image
                        import pytesseract
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                        txt = pytesseract.image_to_string(
                            Image.open(io.BytesIO(pix.tobytes("png"))), lang="eng"
                        )
                        scanned = True
                    texts.append(txt)
                combined = "\n\f\n".join(texts)
                if len(combined.strip()) < 10:
                    raise ValueError("No readable text; upload a clearer scan")
                return OCRResult(text=combined[:150000], language="en",
                                 confidence=0.55 if scanned else 0.98)
            finally:
                pdf.close()
        if mime.startswith("image/") or path.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
            from PIL import Image
            import pytesseract
            image = Image.open(io.BytesIO(content))
            image.verify()
            image = Image.open(io.BytesIO(content)).convert("RGB")
            if image.width * image.height > 24000000:
                raise ValueError("Image exceeds 24 megapixels")
            txt = pytesseract.image_to_string(image, lang="eng")
            if len(txt.strip()) < 10:
                raise ValueError("No readable text; upload a clearer image")
            return OCRResult(text=txt[:150000], confidence=0.5)
        if mime == "text/plain" or path.suffix.lower() == ".txt":
            txt = content.decode("utf-8-sig")
            if not txt.strip():
                raise ValueError("Empty document")
            return OCRResult(text=txt[:150000], confidence=1.0)
        raise ValueError("Unsupported document format")


class RealExtractionProvider:
    def extract(self, text: str, doc_type: DocumentType) -> ExtractionResult:
        result = ExtractionResult(record_date=parsed_date(text))
        for line in text.splitlines():
            line = line.strip()[:300]
            if doc_type == DocumentType.lab_report:
                m = LAB.match(line)
                if m:
                    name = LAB_ALIASES.get(" ".join(m.group(1).lower().split()))
                    if name:
                        value, low, high = float(m.group(2)), float(m.group(4)), float(m.group(5))
                        if 0 <= value < 1000000 and 0 <= low <= high:
                            result.observations.append(ExtractedObservation(
                                test_name=name, value=value, unit=m.group(3),
                                ref_low=low, ref_high=high, effective_date=result.record_date,
                                confidence=0.70,
                            ))
            if doc_type in (DocumentType.prescription, DocumentType.discharge_summary):
                m = RX.match(line)
                if m:
                    result.medications.append(ExtractedMedication(
                        name=m.group(1).strip(), strength=m.group(2).strip(),
                        frequency=m.group(3).strip(), confidence=0.60,
                    ))
        # Diagnoses and prescriptions that are not explicit are never invented.
        return result


class RealSummaryProvider:
    def summarize(self, extraction: ExtractionResult, lang: str) -> SummaryResult:
        language = lang if lang in ("en", "hi", "ta") else "en"
        from app.services.reference_ranges import interpretation_for
        meds = ", ".join(m.name for m in extraction.medications)
        labs = [
            f"{o.test_name}: {o.value:g} {o.unit or ''} ({interpretation_for(o).value})"
            for o in extraction.observations if o.value is not None
        ]
        if language == "hi":
            txt = "रिपोर्ट से निकाली गई जानकारी (जाँच आवश्यक): "
            txt += "; ".join(labs) or "कोई स्पष्ट लैब मान नहीं मिला"
            if meds: txt += "। दर्ज दवाएँ: " + meds
            warning = "यह निदान या उपचार की सलाह नहीं है। मूल रिपोर्ट डॉक्टर से जाँचें।"
        elif language == "ta":
            txt = "அறிக்கையில் இருந்து எடுக்கப்பட்ட தகவல் (சரிபார்க்க வேண்டும்): "
            txt += "; ".join(labs) or "தெளிவான ஆய்வக மதிப்புகள் கிடைக்கவில்லை"
            if meds: txt += ". குறிப்பிடப்பட்ட மருந்துகள்: " + meds
            warning = "இது நோயறிதலோ மருத்துவ ஆலோசனையோ அல்ல. மருத்துவரிடம் சரிபார்க்கவும்."
        else:
            txt = "Transcribed from this report (requires human verification): "
            txt += "; ".join(labs) or "No confidently parsed laboratory values"
            if meds: txt += ". Medicines mentioned: " + meds
            warning = "Not a diagnosis or treatment recommendation. Verify against your original report with a clinician."
        return SummaryResult(plain_text=txt + "\n" + warning,
                             abnormal_explanations=[], language=language,
                             provider="evidence-rules", disclaimer=warning)
