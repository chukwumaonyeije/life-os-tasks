import io
import json
from datetime import datetime
from unittest.mock import MagicMock


def make_mock_row(**kwargs):
    m = MagicMock()
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


def test_export_returns_collections(test_client, mock_db_session):
    # Prepare one item per collection
    raw = make_mock_row(id="r1", source="manual", received_at=datetime(2025,1,1,0,0,0), payload="p", processed=False)
    cand = make_mock_row(id="c1", raw_event_id="r1", created_at=datetime(2025,1,1,0,0,0), title="T1", description="d", priority="medium", status="pending", ai_suggestion_id=None)
    task = make_mock_row(id="t1", created_at=datetime(2025,1,1,0,0,0), title="Task", description="dd", priority="low", status="active", completed_at=None, raw_event_id="r1")
    review = make_mock_row(id="ra1", candidate_id="c1", action="approved", timestamp=datetime(2025,1,1,0,0,0), raw_event_id="r1")
    ai = make_mock_row(id="ai1", provider="prov", model="m1", rationale="r", suggestion_json={"confidence":0.9}, created_at=datetime(2025,1,1,0,0,0))

    # Create query mocks mapping by model class
    def query_side_effect(model):
        qm = MagicMock()
        if model.__name__ == 'RawEvent':
            qm.order_by.return_value.all.return_value = [raw]
        elif model.__name__ == 'TaskCandidate':
            qm.order_by.return_value.all.return_value = [cand]
        elif model.__name__ == 'Task':
            qm.order_by.return_value.all.return_value = [task]
        elif model.__name__ == 'ReviewAction':
            qm.order_by.return_value.all.return_value = [review]
        elif model.__name__ == 'AISuggestion':
            qm.order_by.return_value.all.return_value = [ai]
        else:
            qm.order_by.return_value.all.return_value = []
        return qm

    mock_db_session.query.side_effect = query_side_effect

    res = test_client.get('/api/export')
    assert res.status_code == 200
    data = res.json()
    assert 'raw_events' in data and len(data['raw_events']) == 1
    assert 'task_candidates' in data and len(data['task_candidates']) == 1
    assert 'tasks' in data and len(data['tasks']) == 1
    assert 'review_actions' in data and len(data['review_actions']) == 1
    assert 'ai_suggestions' in data and len(data['ai_suggestions']) == 1


def test_import_preview_and_import(test_client, mock_db_session):
    # Build a sample payload with one task that will collide
    payload = {
        "raw_events": [{"id": "r2", "source": "manual", "received_at": "2025-01-02T00:00:00", "payload": "x", "processed": False}],
        "task_candidates": [{"id": "c2", "raw_event_id": "r2", "created_at": "2025-01-02T00:00:00", "title": "Cand", "description": "d", "priority": "medium", "status": "pending", "ai_suggestion_id": None}],
        "tasks": [{"id": "t-existing", "created_at": "2025-01-02T00:00:00", "title": "Existing Task", "description": "d", "priority": "low", "status": "active", "completed_at": None, "raw_event_id": "r2"}],
        "review_actions": [],
        "ai_suggestions": [],
    }

    # Prepare query mocks for collision detection: Task with id 't-existing' exists
    def query_side_effect(model):
        qm = MagicMock()
        # For collision detection, import preview uses model.id.in_(...)
        if model.__name__ == 'Task':
            existing = make_mock_row(id='t-existing')
            filt = MagicMock()
            filt.all.return_value = [existing]
            qm.filter.return_value = filt
        else:
            filt = MagicMock()
            filt.all.return_value = []
            qm.filter.return_value = filt
        return qm

    mock_db_session.query.side_effect = query_side_effect

    # POST preview
    file_obj = io.BytesIO(json.dumps(payload).encode())
    response = test_client.post('/api/import/preview', files={'file': ('payload.json', file_obj, 'application/json')})
    assert response.status_code == 200
    preview = response.json()
    assert preview['preview']['counts']['tasks'] == 1
    assert 't-existing' in preview['collisions']['tasks']

    # Now test full import: ensure merge and commit are called
    # Reset query side effect for import (not strictly needed)
    mock_db_session.query.side_effect = lambda model: MagicMock()

    file_obj2 = io.BytesIO(json.dumps(payload).encode())
    response2 = test_client.post('/api/import', files={'file': ('payload.json', file_obj2, 'application/json')})
    assert response2.status_code == 200
    data = response2.json()
    assert data['status'] == 'imported'
    # merge should be called multiple times (for raw_events, candidates, tasks)
    assert mock_db_session.merge.call_count >= 1
    mock_db_session.commit.assert_called()
