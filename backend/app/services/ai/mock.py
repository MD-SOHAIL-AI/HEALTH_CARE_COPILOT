"""Realistic mock OCR / extraction / summary providers for demos."""

from datetime import date, timedelta

from app.models.entities import DocumentType, Interpretation
from app.services.ai.base import (
    ExtractedCondition,
    ExtractedEncounter,
    ExtractedMedication,
    ExtractedObservation,
    ExtractionResult,
    OCRResult,
    SummaryResult,
)
from app.services.reference_ranges import enrich_observation, explain_abnormal, interpretation_for


class MockOCRProvider:
    def extract_text(self, file_path: str, mime: str) -> OCRResult:
        name = file_path.lower()
        if "lab" in name or "report" in name:
            text = (
                "CITY DIAGNOSTICS\nLab Report\nDate: 2025-11-12\n"
                "HbA1c: 7.2 % (4.0-5.6)\nFasting Blood Sugar: 132 mg/dL (70-99)\n"
                "Hemoglobin: 11.2 g/dL (12.0-16.0)\nTSH: 5.8 mIU/L (0.4-4.0)\n"
                "Total Cholesterol: 228 mg/dL (<200)\nLDL: 148 mg/dL (<100)\n"
            )
            return OCRResult(text=text, language="en", confidence=0.92)
        if "discharge" in name:
            text = (
                "Apollo Hospital Discharge Summary\nAdmit: 2025-09-01 Discharge: 2025-09-05\n"
                "Diagnosis: Type 2 Diabetes Mellitus with uncontrolled sugars\n"
                "Medications: Metformin 500mg BD, Glimepiride 1mg OD\n"
            )
            return OCRResult(text=text, language="en", confidence=0.88)
        if "rx" in name or "prescription" in name or "rxn" in name:
            text = (
                "Dr. Sharma Clinic\nRx\n1. Metformin 500 mg — 1 tablet twice daily after food x 30 days\n"
                "2. Atorvastatin 10 mg — 1 tablet at night x 30 days\n"
                "3. Vitamin D3 60k IU — once weekly x 4 weeks\nDate: 2025-10-20\n"
            )
            return OCRResult(text=text, language="en", confidence=0.85)
        text = (
            "Diagnostic Imaging Center\nChest X-Ray PA view\nImpression: No acute cardiopulmonary abnormality.\n"
            "Date: 2025-08-15\n"
        )
        return OCRResult(text=text, language="en", confidence=0.9)


class MockExtractionProvider:
    def extract(self, text: str, doc_type: DocumentType) -> ExtractionResult:
        today = date.today()
        if doc_type == DocumentType.prescription:
            return ExtractionResult(
                medications=[
                    ExtractedMedication(
                        name="Metformin",
                        strength="500 mg",
                        dosage="1 tablet",
                        frequency="twice daily",
                        route="oral",
                        duration="30 days",
                        instructions="After food",
                        start_date=today - timedelta(days=20),
                        confidence=0.93,
                    ),
                    ExtractedMedication(
                        name="Atorvastatin",
                        strength="10 mg",
                        dosage="1 tablet",
                        frequency="once daily at night",
                        route="oral",
                        duration="30 days",
                        start_date=today - timedelta(days=20),
                        confidence=0.91,
                    ),
                    ExtractedMedication(
                        name="Vitamin D3",
                        strength="60000 IU",
                        dosage="1 capsule",
                        frequency="once weekly",
                        route="oral",
                        duration="4 weeks",
                        start_date=today - timedelta(days=20),
                        confidence=0.78,
                    ),
                ],
                conditions=[
                    ExtractedCondition(
                        name="Type 2 Diabetes Mellitus",
                        icd10_code="E11",
                        clinical_status="active",
                        onset_date=today - timedelta(days=400),
                        confidence=0.8,
                    )
                ],
                record_date=today - timedelta(days=20),
                source_facility="Dr. Sharma Clinic",
            )

        if doc_type == DocumentType.lab_report:
            obs_raw = [
                ExtractedObservation(
                    test_name="HbA1c",
                    value=7.2,
                    unit="%",
                    effective_date=today - timedelta(days=30),
                    confidence=0.95,
                ),
                ExtractedObservation(
                    test_name="Fasting Blood Sugar",
                    value=132,
                    unit="mg/dL",
                    effective_date=today - timedelta(days=30),
                    confidence=0.94,
                ),
                ExtractedObservation(
                    test_name="Hemoglobin",
                    value=11.2,
                    unit="g/dL",
                    effective_date=today - timedelta(days=30),
                    confidence=0.9,
                ),
                ExtractedObservation(
                    test_name="TSH",
                    value=5.8,
                    unit="mIU/L",
                    effective_date=today - timedelta(days=30),
                    confidence=0.89,
                ),
                ExtractedObservation(
                    test_name="Total Cholesterol",
                    value=228,
                    unit="mg/dL",
                    effective_date=today - timedelta(days=30),
                    confidence=0.92,
                ),
                ExtractedObservation(
                    test_name="LDL",
                    value=148,
                    unit="mg/dL",
                    effective_date=today - timedelta(days=30),
                    confidence=0.91,
                ),
            ]
            observations = [enrich_observation(o) for o in obs_raw]
            return ExtractionResult(
                observations=observations,
                record_date=today - timedelta(days=30),
                source_facility="City Diagnostics",
            )

        if doc_type == DocumentType.discharge_summary:
            return ExtractionResult(
                conditions=[
                    ExtractedCondition(
                        name="Type 2 Diabetes Mellitus with hyperglycemia",
                        icd10_code="E11.65",
                        clinical_status="active",
                        onset_date=today - timedelta(days=60),
                        confidence=0.9,
                    )
                ],
                medications=[
                    ExtractedMedication(
                        name="Metformin",
                        strength="500 mg",
                        dosage="1 tablet",
                        frequency="twice daily",
                        route="oral",
                        duration="ongoing",
                        start_date=today - timedelta(days=55),
                        confidence=0.9,
                    ),
                    ExtractedMedication(
                        name="Glimepiride",
                        strength="1 mg",
                        dosage="1 tablet",
                        frequency="once daily",
                        route="oral",
                        duration="ongoing",
                        start_date=today - timedelta(days=55),
                        confidence=0.88,
                    ),
                ],
                encounters=[
                    ExtractedEncounter(
                        facility="Apollo Hospital",
                        admit_date=today - timedelta(days=60),
                        discharge_date=today - timedelta(days=56),
                        reason="Uncontrolled blood sugars",
                        confidence=0.92,
                    )
                ],
                record_date=today - timedelta(days=56),
                source_facility="Apollo Hospital",
            )

        # diagnostic_report
        return ExtractionResult(
            conditions=[
                ExtractedCondition(
                    name="No acute cardiopulmonary abnormality (Chest X-Ray)",
                    clinical_status="resolved",
                    onset_date=today - timedelta(days=90),
                    confidence=0.86,
                )
            ],
            record_date=today - timedelta(days=90),
            source_facility="Diagnostic Imaging Center",
        )


class MockSummaryProvider:
    def summarize(self, extraction: ExtractionResult, lang: str) -> SummaryResult:
        lang = (lang or "en").lower()
        explanations: list[dict] = []

        for obs in extraction.observations:
            interp = interpretation_for(obs)
            text = explain_abnormal(obs.test_name, interp, lang)
            if text:
                explanations.append(
                    {
                        "test_name": obs.test_name,
                        "value": obs.value,
                        "unit": obs.unit,
                        "interpretation": interp.value,
                        "explanation": text,
                    }
                )

        med_names = ", ".join(m.name for m in extraction.medications) or (
            "कोई दवा नहीं" if lang.startswith("hi") else "no medications listed"
        )
        cond_names = ", ".join(c.name for c in extraction.conditions) or (
            "कोई निदान नहीं" if lang.startswith("hi") else "no diagnoses listed"
        )
        abnormal_count = len(explanations)

        if lang.startswith("hi"):
            plain = (
                f"यह रिकॉर्ड सरल भाषा में सारांशित है।\n\n"
                f"संबंधित स्थितियाँ: {cond_names}.\n"
                f"दवाएँ: {med_names}.\n"
            )
            if extraction.observations:
                plain += f"प्रयोगशाला परिणामों में {abnormal_count} मान सामान्य सीमा से बाहर दिखे।\n"
            if extraction.encounters:
                enc = extraction.encounters[0]
                plain += (
                    f"अस्पताल: {enc.facility or 'अज्ञात'}; "
                    f"भर्ती {enc.admit_date}, छुट्टी {enc.discharge_date}.\n"
                )
            plain += "\nयह निदान नहीं है; अपने चिकित्सक से सलाह लें।"
            disclaimer = "यह निदान नहीं है; अपने चिकित्सक से सलाह लें।"
        else:
            plain = (
                "Here is a plain-language summary of this record.\n\n"
                f"Related conditions: {cond_names}.\n"
                f"Medicines mentioned: {med_names}.\n"
            )
            if extraction.observations:
                plain += (
                    f"Among the lab results, {abnormal_count} value(s) appear outside the usual range. "
                    "See explanations below — these are educational notes, not a diagnosis.\n"
                )
            if extraction.encounters:
                enc = extraction.encounters[0]
                plain += (
                    f"Hospital stay at {enc.facility or 'unknown facility'} "
                    f"(admit {enc.admit_date}, discharge {enc.discharge_date}).\n"
                )
            plain += "\nNot a diagnosis; consult your doctor."
            disclaimer = "Not a diagnosis; consult your doctor."

        return SummaryResult(
            plain_text=plain,
            abnormal_explanations=explanations,
            language="hi" if lang.startswith("hi") else "en",
            provider="mock",
            disclaimer=disclaimer,
        )
