import io
import json


def make_large_payload(n):
    return {
        "raw_events": [
            {"id": f"r{i}", "source": "bulk", "received_at": "2025-01-02T00:00:00", "payload": "x", "processed": False}
            for i in range(n)
        ],
        "task_candidates": [],
        "tasks": [],
        "review_actions": [],
        "ai_suggestions": [],
    }


def test_preview_handles_large_payload(test_client):
    payload = make_large_payload(1000)
    file_obj = io.BytesIO(json.dumps(payload).encode())
    response = test_client.post('/api/import/preview', files={'file': ('bulk.json', file_obj, 'application/json')})
    assert response.status_code == 200
    body = response.json()
    assert body['preview']['counts']['raw_events'] == 1000


def test_import_handles_large_payload_and_merges_all(test_client, mock_db_session):
    payload = make_large_payload(500)
    file_obj = io.BytesIO(json.dumps(payload).encode())
    response = test_client.post('/api/import', files={'file': ('bulk.json', file_obj, 'application/json')})
    assert response.status_code == 200
    # ensure merge called for each incoming raw_event
    total_raw = 500
    # count merge calls where first positional arg is present
    merged_args = [c[0][0] for c in mock_db_session.merge.call_args_list if c[0]]
    raw_merged = [o for o in merged_args if getattr(o, 'id', '').startswith('r')]
    assert len(raw_merged) == total_raw
    # commit should be called once
    assert mock_db_session.commit.call_count == 1


def test_import_handles_invalid_datetime_fields(test_client, mock_db_session):
    payload = {
        "raw_events": [],
        "task_candidates": [],
        "tasks": [
            {"id": "t1", "created_at": "not-a-date", "title": "T", "description": "D", "priority": "low", "status": "open", "completed_at": None, "raw_event_id": None}
        ],
        "review_actions": [],
        "ai_suggestions": [],
    }

    file_obj = io.BytesIO(json.dumps(payload).encode())
    response = test_client.post('/api/import', files={'file': ('payload.json', file_obj, 'application/json')})
    assert response.status_code == 200
    merged_args = [c[0][0] for c in mock_db_session.merge.call_args_list if c[0]]
    objs = [o for o in merged_args if getattr(o, 'id', None) == 't1']
    assert objs, 'No merged Task found for t1'
    obj = objs[0]
    # parse_dt should have converted invalid date -> None
    assert getattr(obj, 'created_at') is None
