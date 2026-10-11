from functools import lru_cache

from app.core.config import get_settings
from app.services.ai.base import ExtractionProvider, OCRProvider, SummaryProvider
from app.services.ai.mock import MockExtractionProvider, MockOCRProvider, MockSummaryProvider


@lru_cache
def get_ocr_provider() -> OCRProvider:
    settings = get_settings()
    # Team can add: if settings.AI_PROVIDER == "team": return TeamOCRProvider()
    return MockOCRProvider()


@lru_cache
def get_extraction_provider() -> ExtractionProvider:
    settings = get_settings()
    _ = settings.AI_PROVIDER
    return MockExtractionProvider()


@lru_cache
def get_summary_provider() -> SummaryProvider:
    settings = get_settings()
    _ = settings.AI_PROVIDER
    return MockSummaryProvider()
