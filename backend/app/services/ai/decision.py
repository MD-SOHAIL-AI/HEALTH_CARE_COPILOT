"""Laya is advisory only. Never gate medical safety or numeric interpretations on its outputs."""
from functools import lru_cache
from app.core.config import get_settings

QUESTIONS = {
    "intent": {
        "type": "choice",
        "instructions": "Which type of medical record question is this?",
        "criteria": {
            "labs": "laboratory measurements, test numbers, trends and reference intervals",
            "medications": "historical prescriptions, medication lists and dosage transcription",
            "history": "patient visit and document chronology",
            "records": "general document searches and report summaries",
        },
    }
}

@lru_cache(maxsize=1)
def _router():
    from laya import Router
    return Router()

def route_question(question: str) -> dict:
    if not get_settings().LAYA_ENABLED:
        return {"status": "disabled", "model": None, "intent": None}
    try:
        result = _router().predict("Question: " + question[:1000], QUESTIONS)
        answer = result.get("answers", {}).get("intent", {})
        label = answer.get("choice")
        conf = float(answer.get("confidence", 0.0))
        if label not in QUESTIONS["intent"]["criteria"] or not 0 <= conf <= 1:
            raise ValueError("Unexpected Laya prediction")
        return {"status": "active", "model": result.get("routing", {}).get("model"),
                "intent": label, "confidence": conf,
                "warning": "Research routing prediction; not medically calibrated"}
    except Exception as exc:
        return {"status": "unavailable", "model": None, "intent": None,
                "reason": type(exc).__name__}
