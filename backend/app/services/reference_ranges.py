"""Rule-based lab reference ranges and interpretation (no AI required)."""

from app.models.entities import Interpretation
from app.services.ai.base import ExtractedObservation

# Common Indian lab ranges (adult general; educational demo only)
REFERENCE_RANGES: dict[str, dict] = {
    "hba1c": {"loinc": "4548-4", "unit": "%", "low": 4.0, "high": 5.6},
    "hemoglobin a1c": {"loinc": "4548-4", "unit": "%", "low": 4.0, "high": 5.6},
    "fasting blood sugar": {"loinc": "1558-6", "unit": "mg/dL", "low": 70, "high": 99},
    "fasting glucose": {"loinc": "1558-6", "unit": "mg/dL", "low": 70, "high": 99},
    "glucose fasting": {"loinc": "1558-6", "unit": "mg/dL", "low": 70, "high": 99},
    "blood glucose": {"loinc": "2339-0", "unit": "mg/dL", "low": 70, "high": 140},
    "hemoglobin": {"loinc": "718-7", "unit": "g/dL", "low": 12.0, "high": 16.0},
    "hb": {"loinc": "718-7", "unit": "g/dL", "low": 12.0, "high": 16.0},
    "tsh": {"loinc": "3016-3", "unit": "mIU/L", "low": 0.4, "high": 4.0},
    "total cholesterol": {"loinc": "2093-3", "unit": "mg/dL", "low": 0, "high": 200},
    "ldl": {"loinc": "2089-1", "unit": "mg/dL", "low": 0, "high": 100},
    "ldl cholesterol": {"loinc": "2089-1", "unit": "mg/dL", "low": 0, "high": 100},
    "hdl": {"loinc": "2085-9", "unit": "mg/dL", "low": 40, "high": 60},
    "hdl cholesterol": {"loinc": "2085-9", "unit": "mg/dL", "low": 40, "high": 60},
    "triglycerides": {"loinc": "2571-8", "unit": "mg/dL", "low": 0, "high": 150},
    "creatinine": {"loinc": "2160-0", "unit": "mg/dL", "low": 0.6, "high": 1.2},
    "vitamin d": {"loinc": "14635-7", "unit": "ng/mL", "low": 30, "high": 100},
    "vitamin b12": {"loinc": "2132-9", "unit": "pg/mL", "low": 200, "high": 900},
}


def _normalize(name: str) -> str:
    return name.strip().lower()


def lookup_range(test_name: str) -> dict | None:
    return REFERENCE_RANGES.get(_normalize(test_name))


def interpret_value(value: float | None, ref_low: float | None, ref_high: float | None) -> Interpretation:
    if value is None or (ref_low is None and ref_high is None):
        return Interpretation.unknown
    if ref_high is not None and value > ref_high:
        return Interpretation.H
    if ref_low is not None and value < ref_low:
        return Interpretation.L
    return Interpretation.N


def enrich_observation(obs: ExtractedObservation) -> ExtractedObservation:
    ref = lookup_range(obs.test_name)
    if ref:
        if obs.ref_low is None:
            obs.ref_low = ref["low"]
        if obs.ref_high is None:
            obs.ref_high = ref["high"]
        if not obs.unit:
            obs.unit = ref["unit"]
        if not obs.loinc_code:
            obs.loinc_code = ref["loinc"]
    return obs


def interpretation_for(obs: ExtractedObservation) -> Interpretation:
    enriched = enrich_observation(obs)
    return interpret_value(enriched.value, enriched.ref_low, enriched.ref_high)


ABNORMAL_EXPLANATIONS_EN = {
    "hba1c": "HbA1c reflects average blood sugar over about 3 months. Values above the usual range may suggest prediabetes or diabetes and should be discussed with a clinician.",
    "fasting blood sugar": "Fasting blood sugar is measured after not eating for several hours. Higher values can indicate impaired glucose control.",
    "hemoglobin": "Hemoglobin carries oxygen in the blood. Low values may relate to anemia; high values have other causes. A clinician can interpret this in context.",
    "tsh": "TSH helps assess thyroid function. Values outside the usual range may need further thyroid tests and medical advice.",
    "total cholesterol": "Total cholesterol is one marker of heart risk. Elevated levels are often managed with lifestyle changes and, if needed, medicines prescribed by a doctor.",
    "ldl": "LDL is sometimes called 'bad' cholesterol. Higher levels may increase cardiovascular risk over time.",
    "hdl": "HDL is sometimes called 'good' cholesterol. Lower levels may reduce protective effect for the heart.",
    "triglycerides": "Triglycerides are a type of fat in the blood. High levels can be linked to diet, diabetes, or other factors.",
    "creatinine": "Creatinine helps estimate kidney function. Values outside the usual range may need follow-up with a clinician.",
    "vitamin d": "Vitamin D supports bone and immune health. Low levels are common and often addressed after medical advice.",
}


ABNORMAL_EXPLANATIONS_HI = {
    "hba1c": "HbA1c पिछले लगभग 3 महीनों का औसत रक्त शर्करा दिखाता है। सामान्य सीमा से अधिक मान प्रीडायबिटीज या डायबिटीज का संकेत हो सकते हैं—डॉक्टर से चर्चा करें।",
    "fasting blood sugar": "उपवास रक्त शर्करा कई घंटे बिना खाए मापी जाती है। अधिक मान ग्लूकोज नियंत्रण की समस्या दिखा सकते हैं।",
    "hemoglobin": "हीमोग्लोबिन रक्त में ऑक्सीजन ले जाता है। कम मान एनीमिया से जुड़ा हो सकता है। चिकित्सक से सलाह लें।",
    "tsh": "TSH थायरॉइड कार्य का आकलन करने में मदद करता है। सीमा से बाहर मान पर आगे जांच की जरूरत हो सकती है।",
    "total cholesterol": "कुल कोलेस्ट्रॉल हृदय जोखिम का एक संकेतक है। ऊँचे स्तर पर जीवनशैली और चिकित्सकीय सलाह महत्वपूर्ण है।",
    "ldl": "LDL को कभी-कभी 'खराब' कोलेस्ट्रॉल कहा जाता है। अधिक स्तर लंबे समय में हृदय जोखिम बढ़ा सकते हैं।",
    "hdl": "HDL को कभी-कभी 'अच्छा' कोलेस्ट्रॉल कहा जाता है। कम स्तर सुरक्षा कम कर सकते हैं।",
    "triglycerides": "ट्राइग्लिसराइड रक्त में एक प्रकार की वसा है। अधिक स्तर आहार या अन्य कारणों से जुड़ सकते हैं।",
    "creatinine": "क्रिएटिनिन गुर्दे के कार्य का अनुमान लगाने में मदद करता है। असामान्य मान पर चिकित्सक से मिलें।",
    "vitamin d": "विटामिन डी हड्डियों और प्रतिरक्षा के लिए महत्वपूर्ण है। कम स्तर आम हैं—चिकित्सकीय सलाह के बाद संबोधित करें।",
}


def explain_abnormal(test_name: str, interpretation: Interpretation, lang: str = "en") -> str | None:
    if interpretation not in (Interpretation.H, Interpretation.L):
        return None
    key = _normalize(test_name)
    # fuzzy match against known keys
    table = ABNORMAL_EXPLANATIONS_HI if lang.startswith("hi") else ABNORMAL_EXPLANATIONS_EN
    for k, v in table.items():
        if k in key or key in k:
            return v
    if lang.startswith("hi"):
        return f"{test_name} सामान्य सीमा से बाहर है। इसका अर्थ समझने के लिए अपने चिकित्सक से बात करें।"
    return f"{test_name} is outside the usual reference range. Discuss what this means for you with your clinician."
