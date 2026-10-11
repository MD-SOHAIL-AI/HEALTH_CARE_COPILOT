from functools import lru_cache

from app.core.config import get_settings
from app.services.ai.base import ExtractionProvider, OCRProvider, SummaryProvider
from app.services.ai.mock import MockExtractionProvider, MockOCRProvider, MockSummaryProvider
from app.services.ai.real import RealExtractionProvider, RealOCRProvider, RealSummaryProvider


@lru_cache
def get_ocr_provider() -> OCRProvider:
    settings = get_settings()
    return MockOCRProvider() if settings.AI_PROVIDER == "mock" else RealOCRProvider()


@lru_cache
def get_extraction_provider() -> ExtractionProvider:
    settings = get_settings()
    return MockExtractionProvider() if settings.AI_PROVIDER == "mock" else RealExtractionProvider()


@lru_cache
def get_summary_provider() -> SummaryProvider:
    settings = get_settings()
    return MockSummaryProvider() if settings.AI_PROVIDER == "mock" else RealSummaryProvider()
