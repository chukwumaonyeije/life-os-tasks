from datetime import datetime, timezone
import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.raw_event import RawEvent
from app.models.task import Task
from app.models.task_candidate import TaskCandidate
from app.models.review_action import ReviewAction
from app.models.ai_suggestion import AISuggestion

router = APIRouter()


def serialize_datetime(v):
    if v is None:
        return None
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v)


@router.get("/api/export")
def export_all(db: Session = Depends(get_db)):
    """Export raw events, candidates, tasks, review actions and AI suggestions as JSON."""
    raw = [
        {
            "id": r.id,
            "source": r.source,
            "received_at": serialize_datetime(r.received_at),
            "payload": r.payload,
            "processed": bool(r.processed),
        }
        for r in db.query(RawEvent).order_by(RawEvent.received_at.asc()).all()
    ]

    candidates = [
        {
            "id": c.id,
            "raw_event_id": c.raw_event_id,
            "created_at": serialize_datetime(c.created_at),
            "title": c.title,
            "description": c.description,
            "priority": c.priority,
            "status": c.status,
            "ai_suggestion_id": c.ai_suggestion_id,
        }
        for c in db.query(TaskCandidate).order_by(TaskCandidate.created_at.asc()).all()
    ]

    tasks = [
        {
            "id": t.id,
            "created_at": serialize_datetime(t.created_at),
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "status": t.status,
            "completed_at": serialize_datetime(t.completed_at),
            "raw_event_id": t.raw_event_id,
        }
        for t in db.query(Task).order_by(Task.created_at.asc()).all()
    ]

    reviews = [
        {
            "id": r.id,
            "candidate_id": r.candidate_id,
            "action": r.action,
            "timestamp": serialize_datetime(r.timestamp),
            "raw_event_id": r.raw_event_id,
        }
        for r in db.query(ReviewAction).order_by(ReviewAction.timestamp.asc()).all()
    ]

    ais = [
        {
            "id": a.id,
            "provider": a.provider,
            "model": a.model,
            "rationale": a.rationale,
            "suggestion_json": a.suggestion_json,
            "created_at": serialize_datetime(a.created_at),
        }
        for a in db.query(AISuggestion).order_by(AISuggestion.created_at.asc()).all()
    ]

    payload = {
        "raw_events": raw,
        "task_candidates": candidates,
        "tasks": tasks,
        "review_actions": reviews,
        "ai_suggestions": ais,
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }

    return payload


@router.post("/api/import")
async def import_all(file: UploadFile = File(...), db: Session = Depends(get_db), overrides: str | None = Form(None)):
    """Import data from a JSON archive produced by `/api/export`.

    This endpoint will attempt to insert records. It uses `merge` semantics so existing
    primary keys are preserved and not duplicated.
    """
    if file.content_type not in ("application/json", "text/json"):
        raise HTTPException(status_code=400, detail="file must be JSON")

    raw_body = await file.read()
    try:
        payload = json.loads(raw_body.decode())
    except Exception:
        raise HTTPException(status_code=400, detail="invalid JSON")

    count = {"raw_events": 0, "task_candidates": 0, "tasks": 0, "review_actions": 0, "ai_suggestions": 0}

    # Helper to parse iso datetimes safely
    def parse_dt(v):
        if not v:
            return None
        try:
            return datetime.fromisoformat(v)
        except Exception:
            return None

    # Parse overrides if provided
    override_map = {}
    if overrides:
        try:
            override_map = json.loads(overrides)
        except Exception:
            raise HTTPException(status_code=400, detail="invalid overrides JSON")

    # Import raw events
    for r in payload.get("raw_events", []):
        # Raw events rarely collide; apply overrides if present
        id_ = r.get('id')
        if id_ and override_map.get('raw_events', {}).get(id_):
            # fetch existing and selectively apply fields
            existing = db.query(RawEvent).filter(RawEvent.id == id_).first()
            fields = ['id', 'source', 'received_at', 'payload', 'processed']
            final = {}
            for f in fields:
                choice = override_map.get('raw_events', {}).get(id_, {}).get(f, 'incoming')
                if existing and choice == 'existing':
                    final[f] = getattr(existing, f, None)
                else:
                    if f == 'received_at':
                        final[f] = parse_dt(r.get('received_at'))
                    elif f == 'processed':
                        final[f] = bool(r.get('processed', False))
                    else:
                        final[f] = r.get(f)
            obj = RawEvent(**final)
        else:
            obj = RawEvent(
                id=r.get("id"),
                source=r.get("source"),
                received_at=parse_dt(r.get("received_at")),
                payload=r.get("payload"),
                processed=bool(r.get("processed", False)),
            )
        db.merge(obj)
        count["raw_events"] += 1

    for c in payload.get("task_candidates", []):
        id_ = c.get('id')
        if id_ and override_map.get('task_candidates', {}).get(id_):
            existing = db.query(TaskCandidate).filter(TaskCandidate.id == id_).first()
            fields = ["id", "raw_event_id", "created_at", "title", "description", "priority", "status", "ai_suggestion_id"]
            final = {}
            for f in fields:
                choice = override_map.get('task_candidates', {}).get(id_, {}).get(f, 'incoming')
                if existing and choice == 'existing':
                    final[f] = getattr(existing, f, None)
                else:
                    final[f] = c.get(f)
            # normalize created_at
            final['created_at'] = parse_dt(final.get('created_at'))
            obj = TaskCandidate(**final)
        else:
            obj = TaskCandidate(
                id=c.get("id"),
                raw_event_id=c.get("raw_event_id"),
                created_at=parse_dt(c.get("created_at")),
                title=c.get("title"),
                description=c.get("description"),
                priority=c.get("priority"),
                status=c.get("status"),
                ai_suggestion_id=c.get("ai_suggestion_id"),
            )
        db.merge(obj)
        count["task_candidates"] += 1

    for t in payload.get("tasks", []):
        id_ = t.get('id')
        if id_ and override_map.get('tasks', {}).get(id_):
            existing = db.query(Task).filter(Task.id == id_).first()
            fields = ["id", "created_at", "title", "description", "priority", "status", "completed_at", "raw_event_id"]
            final = {}
            for f in fields:
                choice = override_map.get('tasks', {}).get(id_, {}).get(f, 'incoming')
                if existing and choice == 'existing':
                    final[f] = getattr(existing, f, None)
                else:
                    final[f] = t.get(f)
            final['created_at'] = parse_dt(final.get('created_at'))
            final['completed_at'] = parse_dt(final.get('completed_at'))
            obj = Task(**final)
        else:
            obj = Task(
                id=t.get("id"),
                created_at=parse_dt(t.get("created_at")),
                title=t.get("title"),
                description=t.get("description"),
                priority=t.get("priority"),
                status=t.get("status"),
                completed_at=parse_dt(t.get("completed_at")),
                raw_event_id=t.get("raw_event_id"),
            )
        db.merge(obj)
        count["tasks"] += 1

    for r in payload.get("review_actions", []):
        id_ = r.get('id')
        if id_ and override_map.get('review_actions', {}).get(id_):
            existing = db.query(ReviewAction).filter(ReviewAction.id == id_).first()
            fields = ["id", "candidate_id", "action", "timestamp", "raw_event_id"]
            final = {}
            for f in fields:
                choice = override_map.get('review_actions', {}).get(id_, {}).get(f, 'incoming')
                if existing and choice == 'existing':
                    final[f] = getattr(existing, f, None)
                else:
                    final[f] = r.get(f)
            final['timestamp'] = parse_dt(final.get('timestamp'))
            obj = ReviewAction(**final)
        else:
            obj = ReviewAction(
                id=r.get("id"),
                candidate_id=r.get("candidate_id"),
                action=r.get("action"),
                timestamp=parse_dt(r.get("timestamp")),
                raw_event_id=r.get("raw_event_id"),
            )
        db.merge(obj)
        count["review_actions"] += 1

    for a in payload.get("ai_suggestions", []):
        id_ = a.get('id')
        if id_ and override_map.get('ai_suggestions', {}).get(id_):
            existing = db.query(AISuggestion).filter(AISuggestion.id == id_).first()
            fields = ["id", "provider", "model", "rationale", "suggestion_json", "created_at"]
            final = {}
            for f in fields:
                choice = override_map.get('ai_suggestions', {}).get(id_, {}).get(f, 'incoming')
                if existing and choice == 'existing':
                    final[f] = getattr(existing, f, None)
                else:
                    final[f] = a.get(f)
            final['created_at'] = parse_dt(final.get('created_at'))
            obj = AISuggestion(**final)
        else:
            obj = AISuggestion(
                id=a.get("id"),
                provider=a.get("provider"),
                model=a.get("model"),
                rationale=a.get("rationale"),
                suggestion_json=a.get("suggestion_json"),
                created_at=parse_dt(a.get("created_at")),
            )
        db.merge(obj)
        count["ai_suggestions"] += 1

    db.commit()

    return {"status": "imported", "counts": count}


@router.post("/api/import/preview")
async def import_preview(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Return a preview summary of an import file: counts and existing ID collisions.

    The preview helps the user decide whether to proceed with the full import.
    """
    if file.content_type not in ("application/json", "text/json"):
        raise HTTPException(status_code=400, detail="file must be JSON")

    raw_body = await file.read()
    try:
        payload = json.loads(raw_body.decode())
    except Exception:
        raise HTTPException(status_code=400, detail="invalid JSON")

    def ids_of(collection_name):
        return {item.get("id") for item in payload.get(collection_name, []) if item.get("id")}

    preview = {}
    preview["counts"] = {k: len(payload.get(k, [])) for k in ["raw_events", "task_candidates", "tasks", "review_actions", "ai_suggestions"]}

    # Check existing IDs in DB to surface collisions
    collisions = {}
    # helper to query existing ids
    def existing_ids(model, ids):
        if not ids:
            return set()
        rows = db.query(model).filter(model.id.in_(list(ids))).all()
        return {getattr(r, 'id') for r in rows}

    raw_ids = ids_of("raw_events")
    cand_ids = ids_of("task_candidates")
    task_ids = ids_of("tasks")
    review_ids = ids_of("review_actions")
    ai_ids = ids_of("ai_suggestions")

    collisions["raw_events"] = list(existing_ids(RawEvent, raw_ids))
    collisions["task_candidates"] = list(existing_ids(TaskCandidate, cand_ids))
    collisions["tasks"] = list(existing_ids(Task, task_ids))
    collisions["review_actions"] = list(existing_ids(ReviewAction, review_ids))
    collisions["ai_suggestions"] = list(existing_ids(AISuggestion, ai_ids))

    # Provide a small sample of incoming items to help the user confirm
    def sample(collection_name, field_keys=("id", "title")):
        arr = payload.get(collection_name, [])
        sample_items = []
        for i, it in enumerate(arr[:5]):
            entry = {k: it.get(k) for k in field_keys if k in it}
            sample_items.append(entry)
        return sample_items

    preview["samples"] = {
        "task_candidates": sample("task_candidates", ("id", "title")),
        "tasks": sample("tasks", ("id", "title")),
        "raw_events": sample("raw_events", ("id", "source")),
    }

    # Compute field-level diffs for collisions
    diffs = {}

    model_field_map = {
        "raw_events": (RawEvent, ["id", "source", "received_at", "payload", "processed"]),
        "task_candidates": (TaskCandidate, ["id", "raw_event_id", "created_at", "title", "description", "priority", "status", "ai_suggestion_id"]),
        "tasks": (Task, ["id", "created_at", "title", "description", "priority", "status", "completed_at", "raw_event_id"]),
        "review_actions": (ReviewAction, ["id", "candidate_id", "action", "timestamp", "raw_event_id"]),
        "ai_suggestions": (AISuggestion, ["id", "provider", "model", "rationale", "suggestion_json", "created_at"]),
    }

    def existing_record_dict(model, record, fields):
        out = {}
        for f in fields:
            val = getattr(record, f, None)
            # serialize datetimes and complex types
            if isinstance(val, datetime):
                out[f] = val.isoformat()
            else:
                out[f] = val
        return out

    def normalize_incoming(item, fields):
        out = {}
        for f in fields:
            out[f] = item.get(f)
        return out

    for coll_name, ids in collisions.items():
        if not ids:
            continue
        model, fields = model_field_map.get(coll_name, (None, []))
        if model is None:
            continue
        diffs[coll_name] = {}
        # fetch all existing records for these ids
        existing_rows = db.query(model).filter(model.id.in_(ids)).all() if ids else []
        existing_map = {getattr(r, 'id'): existing_record_dict(model, r, fields) for r in existing_rows}

        # incoming items keyed by id
        incoming_map = {it.get('id'): normalize_incoming(it, fields) for it in payload.get(coll_name, []) if it.get('id') in ids}

        for id_ in ids:
            ex = existing_map.get(id_)
            inc = incoming_map.get(id_)
            if ex is None or inc is None:
                continue
            field_diffs = {}
            for f in fields:
                a = ex.get(f)
                b = inc.get(f)
                # for suggestion_json compare via JSON string
                if f == 'suggestion_json':
                    a_s = json.dumps(a, sort_keys=True) if a is not None else None
                    b_s = json.dumps(b, sort_keys=True) if b is not None else None
                    if a_s != b_s:
                        field_diffs[f] = {"existing": a, "incoming": b}
                else:
                    if a != b:
                        field_diffs[f] = {"existing": a, "incoming": b}
            if field_diffs:
                diffs[coll_name][id_] = field_diffs

    preview["diffs"] = diffs

    return {"preview": preview, "collisions": collisions}
