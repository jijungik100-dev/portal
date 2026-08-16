from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    """GET /health 가 200과 ok를 반환하는지 확인."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "hello atlas"}
