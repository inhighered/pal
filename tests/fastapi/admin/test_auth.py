import pytest
from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as client:
        return client


def test_clear_index(client: TestClient):
    response = client.get("/admin/clear_index")

    assert response.status_code == 200
    assert response.text == """<div id="index_content"> Index Cleared </div></br>"""