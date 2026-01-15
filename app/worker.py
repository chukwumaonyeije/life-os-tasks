import logging
import os
import time

from app.ai.contract import suggestion_to_dict
from app.ai.factory import get_suggester
from app.ai.prompts import CURRENT_PROMPT_VERSION, redact_pii, truncate_for_excerpt
from app.core.db import SessionLocal
from app.core.logging_config import setup_logging
from app.core.queue import pop_raw_event
from app.core.summarizer import summarize
from app.models.ai_suggestion import AISuggestion as AISuggestionModel
from app.models.raw_event import RawEvent
from app.models.summary import Summary
from app.models.task_candidate import TaskCandidate

logger = logging.getLogger(__name__)


def process_event(db, raw_event_id: str):
    event = db.query(RawEvent).filter(RawEvent.id == raw_event_id).first()
    if not event or event.processed:
        return

    # Only process dictation events
    if event.source != "dictation":
        event.processed = True
        db.commit()
        return

    # Try AI suggestion first (if enabled)
    suggester = get_suggester()
    if suggester:
        try:
            logger.info(f"Attempting AI suggestion for event {raw_event_id}")

            # Redact PII before sending to AI
            redacted_text = redact_pii(event.payload)

            # Get AI suggestion
            suggestion = suggester.suggest(redacted_text)

            if suggestion:
                logger.info(f"AI suggestion successful: {suggestion.title}")

                # Persist AI evidence
                ai_record = AISuggestionModel(
                    raw_event_id=event.id,
                    provider=suggester.provider_name,
                    model=suggester.model_name,
                    prompt_version=CURRENT_PROMPT_VERSION,
                    input_excerpt=truncate_for_excerpt(event.payload),
                    suggestion_json=suggestion_to_dict(suggestion),
                    rationale=suggestion.rationale,
                )
                db.add(ai_record)
                db.flush()  # Get ai_record.id

                # Create task candidate with AI link
                candidate = TaskCandidate(
                    raw_event_id=event.id,
                    title=suggestion.title,
                    description=suggestion.description,
                    priority=suggestion.priority,
                    ai_suggestion_id=ai_record.id,
                )
                db.add(candidate)

                # Create summary for dictation
                summary = Summary(raw_event_id=event.id, content=event.payload)
                db.add(summary)

                event.processed = True
                db.commit()
                logger.info(f"AI suggestion persisted for event {raw_event_id}")
                return

        except Exception as e:
            logger.error(f"AI suggestion failed for {raw_event_id}: {e}")
            db.rollback()
            # Fall through to stub

    # Fallback: Use stub summarizer (existing behavior)
    logger.info(f"Using stub summarizer for event {raw_event_id}")
    result = summarize(event.payload)

    summary = Summary(raw_event_id=event.id, content=result["summary"])
    db.add(summary)

    for t in result["tasks"]:
        candidate = TaskCandidate(
            raw_event_id=event.id, title=t["title"], description=t["description"]
        )
        db.add(candidate)

    event.processed = True
    db.commit()


def run_worker():
    # Configure logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(log_level)

    logger.info("Worker started")
    while True:
        job = pop_raw_event()
        if not job:
            time.sleep(0.5)
            continue

        raw_event_id = job["raw_event_id"]
        db = SessionLocal()
        try:
            process_event(db, raw_event_id)
        finally:
            db.close()


if __name__ == "__main__":
    run_worker()
