import json
import redis

REDIS_URL = "redis://localhost:6379/0"
QUEUE_NAME = "lifeos:raw_events"

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def enqueue_raw_event(raw_event_id: str):
    payload = {"raw_event_id": raw_event_id}
    redis_client.lpush(QUEUE_NAME, json.dumps(payload))

def pop_raw_event(timeout: int = 2):
    item = redis_client.brpop(QUEUE_NAME, timeout=timeout)
    if item is None:
        return None
    _, data = item
    return json.loads(data)
