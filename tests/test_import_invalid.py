import io
import json


def test_preview_rejects_non_json_content_type(test_client):
    file_obj = io.BytesIO(b'not a json')
    # send as text/plain -> should be rejected
    response = test_client.post('/api/import/preview', files={'file': ('payload.txt', file_obj, 'text/plain')})
    assert response.status_code == 400
    assert 'file must be JSON' in response.json().get('detail', '')


def test_preview_rejects_malformed_json(test_client):
    file_obj = io.BytesIO(b'{"raw_events": [invalid}')
    response = test_client.post('/api/import/preview', files={'file': ('payload.json', file_obj, 'application/json')})
    assert response.status_code == 400
    assert 'invalid JSON' in response.json().get('detail', '')


def test_import_rejects_non_json_content_type(test_client):
    file_obj = io.BytesIO(b'not a json')
    response = test_client.post('/api/import', files={'file': ('payload.txt', file_obj, 'text/plain')})
    assert response.status_code == 400
    assert 'file must be JSON' in response.json().get('detail', '')


def test_import_rejects_malformed_json(test_client):
    file_obj = io.BytesIO(b'')
    response = test_client.post('/api/import', files={'file': ('payload.json', file_obj, 'application/json')})
    assert response.status_code == 400
    assert 'invalid JSON' in response.json().get('detail', '')
