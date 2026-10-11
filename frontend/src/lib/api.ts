import axios from 'axios'
import type {
  Condition,
  Dashboard,
  Document,
  DocumentType,
  LabTrend,
  Medication,
  Observation,
  Patient,
  Summary,
  TimelineEvent,
  User,
} from './types'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const api = axios.create({
  baseURL: `${API_URL}/api`,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('medcare_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function register(data: {
  email: string
  password: string
  full_name: string
  preferred_language?: string
}) {
  const res = await api.post<{ access_token: string }>('/auth/register', data)
  return res.data
}

export async function login(email: string, password: string) {
  const res = await api.post<{ access_token: string }>('/auth/login/json', { email, password })
  return res.data
}

export async function getMe() {
  const res = await api.get<User>('/auth/me')
  return res.data
}

export async function getPatient() {
  const res = await api.get<Patient>('/patients/me')
  return res.data
}

export async function updatePatient(data: Partial<Patient>) {
  const res = await api.patch<Patient>('/patients/me', data)
  return res.data
}

export async function getDashboard() {
  const res = await api.get<Dashboard>('/patients/me/dashboard')
  return res.data
}

export async function listDocuments() {
  const res = await api.get<Document[]>('/documents')
  return res.data
}

export async function getDocument(id: number) {
  const res = await api.get<Document>(`/documents/${id}`)
  return res.data
}

export async function uploadDocument(params: {
  file: File
  doc_type: DocumentType
  record_date?: string
  source_facility?: string
}) {
  const form = new FormData()
  form.append('file', params.file)
  form.append('doc_type', params.doc_type)
  if (params.record_date) form.append('record_date', params.record_date)
  if (params.source_facility) form.append('source_facility', params.source_facility)
  const res = await api.post<Document>('/documents', form)
  return res.data
}

export async function confirmDocument(id: number, body: Record<string, unknown> = {}) {
  const res = await api.post<Document>(`/documents/${id}/confirm`, body)
  return res.data
}

export async function reprocessDocument(id: number) {
  const res = await api.post<Document>(`/documents/${id}/reprocess`)
  return res.data
}

export function documentFileUrl(id: number) {
  const token = localStorage.getItem('medcare_token')
  return `${API_URL}/api/documents/${id}/file?token=${token || ''}`
}

export async function fetchDocumentBlob(id: number) {
  const res = await api.get(`/documents/${id}/file`, { responseType: 'blob' })
  return res.data as Blob
}

export async function listMedications(activeOnly = false) {
  const res = await api.get<Medication[]>('/medications', { params: { active_only: activeOnly } })
  return res.data
}

export async function listObservations() {
  const res = await api.get<Observation[]>('/observations')
  return res.data
}

export async function getTrends() {
  const res = await api.get<LabTrend[]>('/observations/trends')
  return res.data
}

export async function listConditions() {
  const res = await api.get<Condition[]>('/conditions')
  return res.data
}

export async function getTimeline(kind?: string) {
  const res = await api.get<TimelineEvent[]>('/timeline', { params: kind ? { kind } : {} })
  return res.data
}

export async function getDocumentSummary(documentId: number, language: string) {
  const res = await api.get<Summary>(`/summaries/document/${documentId}`, {
    params: { language },
  })
  return res.data
}

export async function linkAbha(abha_number: string, otp: string) {
  const res = await api.post('/abha/link', { abha_number, otp })
  return res.data
}

export async function importAbhaSample() {
  const res = await api.post<Patient>('/abha/import', { use_sample: true })
  return res.data
}

export async function exportFhirBundle() {
  const res = await api.get('/fhir/me/$everything')
  return res.data
}
