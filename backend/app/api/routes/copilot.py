"""Patient-scoped evidence-first medical-record Copilot."""
import re
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.api.deps import get_current_patient
from app.core.database import get_db
from app.models.entities import Patient, Document, DocumentStatus, Observation, Medication
from app.services.ai.decision import route_question

router = APIRouter(prefix="/copilot", tags=["copilot"])
STOP = set("the what about please show with that your from have were where when this which".split())

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    language: str = Field(default="en", pattern="^(en|ta|hi)$")

def tokens(s):
    s = s.lower().replace("haemoglobin","hemoglobin").replace("hgb","hemoglobin").replace("fbs","glucose")
    s = s.replace("blood sugar","glucose").replace("ஹீமோகுளோபின்", "hemoglobin").replace("மருந்து","medicine")
    return {w for w in re.findall(r"[a-z0-9]+",s) if len(w)>2 and w not in STOP}

@router.post("/ask")
def ask(payload: AskRequest, patient: Patient=Depends(get_current_patient), db: Session=Depends(get_db)):
    decision=route_question(payload.question)
    q=tokens(payload.question)
    docs=db.query(Document).filter(Document.patient_id==patient.id,Document.status==DocumentStatus.confirmed).order_by(Document.created_at.desc()).limit(150).all()
    ranked=[]
    for d in docs:
        for page_number,page in enumerate((d.ocr_text or "").split("\f"),1):
            lines=[line.strip() for line in page.splitlines() if line.strip()]
            for start in range(0,len(lines),6):
                chunk="\n".join(lines[start:start+8])[:900]
                score=len(q & tokens(chunk))
                if score: ranked.append((score,{"document_id":d.id,"title":d.original_filename,"excerpt":chunk,"page":page_number}))
    ranked.sort(key=lambda x:x[0],reverse=True)
    citations=[c for _,c in ranked[:6]]
    observations=db.query(Observation, Document).join(Document,Observation.document_id==Document.id).filter(Observation.patient_id==patient.id,Observation.verified.is_(True),Document.patient_id==patient.id,Document.status==DocumentStatus.confirmed).all()
    matched=sorted([(o,d) for o,d in observations if q & tokens(o.test_name)],key=lambda x:(str(x[0].effective_date or ""),x[0].id))
    if matched:
        lines=[];citations=[]
        for o,d in matched[-8:]:
            if o.value is None: continue
            lines.append(str(o.effective_date or "undated")+": "+str(o.value)+" "+str(o.unit or "")+" (report range: "+str(o.ref_low)+" to "+str(o.ref_high)+")")
            citations.append({"document_id":d.id,"title":d.original_filename,"excerpt":lines[-1],"page":None})
        answer="Verified observations from your records:\n"+"\n".join(lines)
        comparable=[o for o,d in matched if o.value is not None]
        if len(comparable)>1 and len({o.unit for o in comparable})==1:
            answer+="\nFirst-to-last difference: "+str(round(comparable[-1].value-comparable[0].value,4))+" "+str(comparable[-1].unit or "")
    elif q & {"medicine","medication","medications","medicines","drug","tablet","prescription","dose"}:
        meds=db.query(Medication,Document).join(Document,Medication.document_id==Document.id).filter(Medication.patient_id==patient.id,Medication.verified.is_(True),Document.patient_id==patient.id,Document.status==DocumentStatus.confirmed).limit(12).all()
        answer="Historical verified prescription entries:\n"+"\n".join(m.name+" "+str(m.strength or "")+" "+str(m.frequency or "") for m,d in meds) if meds else "No verified medications available."
        citations=[{"document_id":d.id,"title":d.original_filename,"excerpt":m.name+" "+str(m.strength or ""),"page":None} for m,d in meds]
    elif citations:
        answer="Matching medical-record excerpts:\n"+"\n".join("["+str(i+1)+"] "+c["title"]+": "+c["excerpt"][:200] for i,c in enumerate(citations[:4]))
    else:
        answer="Insufficient verified evidence. Upload, review and confirm the relevant medical report."
    if payload.language=="ta": answer="உங்கள் பதிவுகளிலிருந்து தகவல்:\n"+answer
    if payload.language=="hi": answer="आपके मेडिकल रिकॉर्ड की जानकारी:\n"+answer
    return {"answer":answer,"citations":citations,"decision":decision,"generation":{"status":"disabled"},"evidence_count":len(ranked),"disclaimer":"Educational record organization only; not diagnosis or treatment advice."}
