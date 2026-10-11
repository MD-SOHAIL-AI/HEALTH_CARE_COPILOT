export type DocumentType =
  | 'prescription'
  | 'lab_report'
  | 'discharge_summary'
  | 'diagnostic_report'

export type DocumentStatus =
  | 'uploaded'
  | 'processing'
  | 'needs_review'
  | 'confirmed'
  | 'failed'

export type Interpretation = 'H' | 'L' | 'N' | 'unknown'

export interface User {
  id: number
  email: string
  full_name: string
  created_at: string
}

export interface Patient {
  id: number
  fhir_id: string
  name: string
  gender: string
  date_of_birth: string | null
  phone: string | null
  abha_number: string | null
  abha_address: string | null
  preferred_language: string
  allergies: string | null
  created_at: string
  updated_at: string
}

export interface Medication {
  id: number
  fhir_id: string
  document_id: number | null
  name: string
  strength: string | null
  dosage: string | null
  frequency: string | null
  route: string | null
  duration: string | null
  instructions: string | null
  start_date: string | null
  end_date: string | null
  is_active: boolean
  confidence: number
  verified: boolean
}

export interface Observation {
  id: number
  fhir_id: string
  document_id: number | null
  test_name: string
  loinc_code: string | null
  value: number | null
  value_text: string | null
  unit: string | null
  ref_low: number | null
  ref_high: number | null
  interpretation: Interpretation
  effective_date: string | null
  confidence: number
  verified: boolean
}

export interface Condition {
  id: number
  fhir_id: string
  document_id: number | null
  name: string
  icd10_code: string | null
  clinical_status: string
  onset_date: string | null
  confidence: number
  verified: boolean
}

export interface Encounter {
  id: number
  fhir_id: string
  document_id: number | null
  facility: string | null
  admit_date: string | null
  discharge_date: string | null
  reason: string | null
  confidence: number
  verified: boolean
}

export interface Summary {
  id: number
  document_id: number
  language: string
  plain_text: string
  abnormal_explanations: Array<{
    test_name: string
    value?: number
    unit?: string
    interpretation?: string
    explanation: string
  }> | null
  provider: string
  disclaimer: string
  created_at: string
}

export interface Document {
  id: number
  fhir_id: string
  doc_type: DocumentType
  original_filename: string
  mime_type: string
  status: DocumentStatus
  record_date: string | null
  source_facility: string | null
  ocr_text: string | null
  ocr_confidence: number | null
  ocr_language: string | null
  error_message: string | null
  created_at: string
  updated_at: string
  medications: Medication[]
  observations: Observation[]
  conditions: Condition[]
  encounters: Encounter[]
  summaries: Summary[]
}

export interface TimelineEvent {
  id: number
  event_date: string
  kind: string
  title: string
  description: string | null
  ref_type: string
  ref_id: number
  document_id: number | null
}

export interface Dashboard {
  patient: Patient
  active_medications: Medication[]
  recent_abnormal: Observation[]
  latest_summary: Summary | null
  recent_documents: Document[]
  document_counts: Record<string, number>
}

export interface LabTrend {
  test_name: string
  unit: string | null
  ref_low: number | null
  ref_high: number | null
  points: Array<{
    effective_date: string | null
    value: number | null
    unit: string | null
    interpretation: Interpretation
    document_id: number | null
  }>
}
