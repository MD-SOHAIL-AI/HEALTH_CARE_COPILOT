"""Seed a demo patient with sample confirmed health data for demos."""

from datetime import date, timedelta
from pathlib import Path

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.entities import (
    Condition,
    Document,
    DocumentStatus,
    DocumentType,
    Encounter,
    Gender,
    Interpretation,
    Medication,
    Observation,
    Patient,
    Summary,
    TimelineEvent,
    TimelineKind,
    User,
)
from app.services.pipeline import process_document
import app.models  # noqa: F401


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "demo@medcare.app").first()
        if existing:
            print("Demo user already exists: demo@medcare.app / demo1234")
            return

        user = User(
            email="demo@medcare.app",
            hashed_password=hash_password("demo1234"),
            full_name="Priya Sharma",
        )
        db.add(user)
        db.flush()

        patient = Patient(
            user_id=user.id,
            name="Priya Sharma",
            gender=Gender.female,
            date_of_birth=date(1992, 4, 12),
            phone="+91-9876543210",
            preferred_language="en",
            allergies="Penicillin",
        )
        db.add(patient)
        db.flush()

        uploads = Path("./uploads")
        uploads.mkdir(parents=True, exist_ok=True)

        samples = [
            ("prescription_rx.txt", DocumentType.prescription, "Sample Rx text"),
            ("lab_report.txt", DocumentType.lab_report, "Sample lab text"),
            ("discharge_summary.txt", DocumentType.discharge_summary, "Sample discharge"),
            ("diagnostic_xray.txt", DocumentType.diagnostic_report, "Sample diagnostic"),
        ]

        for filename, doc_type, content in samples:
            path = uploads / filename
            path.write_text(content, encoding="utf-8")
            doc = Document(
                patient_id=patient.id,
                doc_type=doc_type,
                original_filename=filename,
                file_path=str(path),
                mime_type="text/plain",
                status=DocumentStatus.uploaded,
            )
            db.add(doc)
            db.commit()
            process_document(db, doc.id)
            doc = db.get(Document, doc.id)
            if doc and doc.status == DocumentStatus.needs_review:
                # Confirm for demo readiness
                from app.services.pipeline import confirm_document

                confirm_document(db, doc)

        # Extra historical lab point for trends
        db.add(
            Observation(
                patient_id=patient.id,
                test_name="HbA1c",
                loinc_code="4548-4",
                value=6.8,
                unit="%",
                ref_low=4.0,
                ref_high=5.6,
                interpretation=Interpretation.H,
                effective_date=date.today() - timedelta(days=180),
                confidence=1.0,
                verified=True,
            )
        )
        db.commit()
        print("Seeded demo user: demo@medcare.app / demo1234")
    finally:
        db.close()


if __name__ == "__main__":
    main()
