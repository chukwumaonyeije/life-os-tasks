import hashlib
import hmac
import time

from fastapi import HTTPException

SLACK_SIGNING_SECRET = None  # set later via env


def verify_slack_signature(raw_body: bytes, timestamp: str, signature: str):
    if SLACK_SIGNING_SECRET is None:
        return  # allow local dev without Slack

    if abs(time.time() - int(timestamp)) > 300:
        raise HTTPException(status_code=401, detail="Stale Slack request")

    base = f"v0:{timestamp}:".encode() + raw_body
    digest = hmac.new(SLACK_SIGNING_SECRET.encode(), base, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(f"v0={digest}", signature):
        raise HTTPException(status_code=401, detail="Invalid Slack signature")
