from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime
import os
from app.core.db import engine, get_db
from app.core.logging_config import setup_logging
from app.models.task import Base as TaskBase, Task
from app.models.raw_event import Base as RawBase, RawEvent
from app.models.summary import Base as SummaryBase
from app.models.task_candidate import Base as CandidateBase
from app.models.review_action import Base as ReviewBase, ReviewAction
from app.models.ai_suggestion import Base as AISuggestionBase
from app.ingest_slack import router as slack_router
from app.ingest_dictation import router as dictation_router
from app.api_review import router as review_router

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level)

app = FastAPI(title="LifeOS Tasks")

TaskBase.metadata.create_all(bind=engine)
RawBase.metadata.create_all(bind=engine)
SummaryBase.metadata.create_all(bind=engine)
CandidateBase.metadata.create_all(bind=engine)
ReviewBase.metadata.create_all(bind=engine)
AISuggestionBase.metadata.create_all(bind=engine)

app.include_router(slack_router)
app.include_router(dictation_router)
app.include_router(review_router)

@app.get("/api/tasks")
def list_tasks(status: str = "active", db: Session = Depends(get_db)):
    query = db.query(Task)
    if status != "all":
        query = query.filter(Task.status == status)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    
    # Enrich with source information from raw_events
    result = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "raw_event_id": task.raw_event_id,
            "source": "manual"  # default
        }
        
        # Get source from raw_event if exists
        if task.raw_event_id:
            raw_event = db.query(RawEvent).filter(RawEvent.id == task.raw_event_id).first()
            if raw_event:
                task_dict["source"] = raw_event.source
        
        result.append(task_dict)
    
    return result

@app.post("/api/tasks")
def create_task(task: dict, db: Session = Depends(get_db)):
    t = Task(
        title=task["title"],
        description=task.get("description",""),
        priority=task.get("priority","medium")
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

@app.get("/api/inbox")
def get_inbox(db: Session = Depends(get_db)):
    return (
        db.query(RawEvent)
        .order_by(RawEvent.received_at.desc())
        .limit(50)
        .all()
    )

@app.post("/api/inbox")
def add_raw_event(event: dict, db: Session = Depends(get_db)):
    e = RawEvent(
        source=event.get("source", "manual"),
        payload=event["payload"]
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e

@app.post("/api/tasks/{task_id}/complete")
def complete_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "completed"
    task.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    
    return {
        "status": "completed",
        "task_id": task.id,
        "message": "Task marked as complete"
    }

@app.post("/api/tasks/{task_id}/archive")
def archive_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "archived"
    db.commit()
    db.refresh(task)
    
    return {
        "status": "archived",
        "task_id": task.id,
        "message": "Task archived"
    }

@app.post("/api/tasks/{task_id}/reactivate")
def reactivate_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "active"
    task.completed_at = None
    db.commit()
    db.refresh(task)
    
    return {
        "status": "active",
        "task_id": task.id,
        "message": "Task reactivated"
    }

app.mount("/", StaticFiles(directory="static", html=True), name="static")
