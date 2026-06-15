from fastapi.testclient import TestClient

from desktop_app.python_sidecar.desktop_server import create_desktop_app


def test_desktop_sidecar_serves_fallback_and_api(tmp_path):
    client = TestClient(create_desktop_app(frontend_dir=tmp_path))

    index_response = client.get("/")
    assert index_response.status_code == 200
    assert "AI Knowledge Crawler Desktop" in index_response.text

    health_response = client.get("/api/health")
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}
