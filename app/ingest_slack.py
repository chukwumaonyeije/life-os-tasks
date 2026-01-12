import json
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.raw_event import RawEvent
from app.core.security import verify_slack_signature
from app.core.queue import enqueue_raw_event

router = APIRouter()

@router.post("/ingest/slack/events")
async def ingest_slack(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()
    payload = json.loads(raw_body.decode())

    # Slack URL verification handshake
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}

    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")
    verify_slack_signature(raw_body, timestamp, signature)

    event = RawEvent(
        source="slack",
        payload=json.dumps(payload)
    )
    db.add(event)
    db.commit()

    enqueue_raw_event(event.id)

    return {"ok": True}
