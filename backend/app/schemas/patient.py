from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.entities import Gender


class PatientOut(BaseModel):
    id: int
    fhir_id: str
    name: str
    gender: Gender
    date_of_birth: date | None
    phone: str | None
    abha_number: str | None
    abha_address: str | None
    preferred_language: str
    allergies: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatientUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    gender: Gender | None = None
    date_of_birth: date | None = None
    phone: str | None = None
    preferred_language: str | None = None
    allergies: str | None = None


class AbhaLinkRequest(BaseModel):
    abha_number: str = Field(min_length=10, max_length=32)
    otp: str = Field(min_length=4, max_length=8)


class AbhaLinkResponse(BaseModel):
    abha_number: str
    abha_address: str
    message: str


class AbhaImportRequest(BaseModel):
    bundle: dict | None = None
    use_sample: bool = True
