from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.db import get_db
from app.models.task_candidate import TaskCandidate
from app.models.task import Task
from app.models.review_action import ReviewAction
from app.models.ai_suggestion import AISuggestion

router = APIRouter()

@router.get("/api/review")
def get_review_queue(db: Session = Depends(get_db)):
    """Get pending task candidates with AI metadata.
    
    Returns list of candidates with optional AI suggestion metadata:
    - If ai_suggestion_id is present, includes provider, model, rationale, confidence
    - If manual candidate, ai_metadata is None
    """
    candidates = (
        db.query(TaskCandidate)
        .filter(TaskCandidate.status == "pending")
        .order_by(TaskCandidate.created_at.desc())
        .all()
    )
    
    result = []
    for c in candidates:
        item = {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "priority": c.priority,
            "created_at": c.created_at.isoformat(),
            "ai_metadata": None
        }
        
        # Fetch AI metadata if this is an AI-generated candidate
        if c.ai_suggestion_id:
            ai_record = db.query(AISuggestion).filter(
                AISuggestion.id == c.ai_suggestion_id
            ).first()
            
            if ai_record:
                item["ai_metadata"] = {
                    "provider": ai_record.provider,
                    "model": ai_record.model,
                    "rationale": ai_record.rationale,
                    "confidence": ai_record.suggestion_json.get("confidence", 0.0)
                }
        
        result.append(item)
    
    return result

@router.post("/api/review/{candidate_id}/approve")
def approve(candidate_id: str, db: Session = Depends(get_db)):
    c = db.query(TaskCandidate).filter(TaskCandidate.id == candidate_id).first()
    if not c:
        return {"error": "Not found", "message": "Candidate not found"}

    # Create audit record (immutable ledger)
    audit = ReviewAction(
        candidate_id=c.id,
        action="approved",
        raw_event_id=c.raw_event_id
    )
    db.add(audit)

    # Create task
    task = Task(
        title=c.title,
        description=c.description,
        raw_event_id=c.raw_event_id
    )
    c.status = "approved"
    db.add(task)
    
    try:
        db.commit()
        db.refresh(task)
    except IntegrityError as e:
        db.rollback()
        # Idempotency violation: task already exists for this raw_event
        if "idx_tasks_raw_event_unique" in str(e):
            return {
                "error": "Duplicate",
                "message": "Task already exists for this event"
            }
        raise
    
    return {
        "status": "approved",
        "task_id": task.id,
        "raw_event_id": c.raw_event_id,
        "message": "Task created successfully"
    }

@router.post("/api/review/{candidate_id}/reject")
def reject(candidate_id: str, db: Session = Depends(get_db)):
    c = db.query(TaskCandidate).filter(TaskCandidate.id == candidate_id).first()
    if not c:
        return {"error": "Not found", "message": "Candidate not found"}
    
    # Create audit record (immutable ledger)
    audit = ReviewAction(
        candidate_id=c.id,
        action="rejected",
        raw_event_id=c.raw_event_id
    )
    db.add(audit)
    
    c.status = "rejected"
    db.commit()
    
    return {
        "status": "rejected",
        "candidate_id": c.id,
        "message": "Candidate dismissed"
    }

@router.get("/api/review/approved")
def get_recently_approved(db: Session = Depends(get_db)):
    return (
        db.query(TaskCandidate)
        .filter(TaskCandidate.status == "approved")
        .order_by(TaskCandidate.created_at.desc())
        .limit(10)
        .all()
    )
