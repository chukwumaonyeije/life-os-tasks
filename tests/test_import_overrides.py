import io
import json
from unittest.mock import MagicMock


def test_import_respects_field_overrides_for_tasks(test_client, mock_db_session):
    """When overrides specify existing for a field, the merged object keeps the existing value."""
    from app.models.task import Task

    # Incoming payload with one task
    payload = {
        "raw_events": [],
        "task_candidates": [],
        "tasks": [
            {
                "id": "t1",
                "created_at": "2025-01-02T00:00:00",
                "title": "Incoming Title",
                "description": "Incoming Desc",
                "priority": "high",
                "status": "active",
                "completed_at": None,
                "raw_event_id": None,
            }
        ],
        "review_actions": [],
        "ai_suggestions": [],
    }

    # Existing record in DB with different title
    existing = MagicMock()
    existing.id = 't1'
    existing.title = 'Existing Title'
    existing.description = 'Existing Desc'
    existing.priority = 'low'
    existing.status = 'active'

    # Configure query side effect: Task queries return the existing record for filter().first()
    def query_side_effect(model):
        qm = MagicMock()
        if model.__name__ == 'Task':
            filt = MagicMock()
            filt.first.return_value = existing
            qm.filter.return_value = filt
        else:
            filt = MagicMock()
            filt.first.return_value = None
            qm.filter.return_value = filt
        return qm

    mock_db_session.query.side_effect = query_side_effect

    overrides = {"tasks": {"t1": {"title": "existing", "description": "incoming"}}}

    file_obj = io.BytesIO(json.dumps(payload).encode())
    response = test_client.post('/api/import', data={'overrides': json.dumps(overrides)}, files={'file': ('payload.json', file_obj, 'application/json')})
    assert response.status_code == 200
    # Find the Task object passed to merge
    merged_args = [c[0][0] for c in mock_db_session.merge.call_args_list if c[0]]
    task_objs = [o for o in merged_args if getattr(o, 'id', None) == 't1']
    assert task_objs, 'No merged Task found for t1'
    task_obj = task_objs[0]
    # Title should be from existing, description from incoming
    assert task_obj.title == 'Existing Title'
    assert task_obj.description == 'Incoming Desc'
