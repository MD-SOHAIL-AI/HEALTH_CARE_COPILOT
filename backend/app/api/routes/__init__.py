from fastapi import APIRouter

from app.api.routes import abha, auth, conditions, documents, fhir, medications, observations, patients, summaries, timeline

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(patients.router)
api_router.include_router(documents.router)
api_router.include_router(medications.router)
api_router.include_router(observations.router)
api_router.include_router(conditions.router)
api_router.include_router(timeline.router)
api_router.include_router(summaries.router)
api_router.include_router(abha.router)
api_router.include_router(fhir.router)
