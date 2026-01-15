from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.queue import enqueue_raw_event
from app.models.raw_event import RawEvent

router = APIRouter()


@router.post("/ingest/dictation")
def ingest_dictation(body: dict, db: Session = Depends(get_db)):
    event = RawEvent(source="dictation", payload=body["text"])
    db.add(event)
    db.commit()

    enqueue_raw_event(event.id)

    return {"ok": True}
