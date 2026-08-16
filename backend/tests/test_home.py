from fastapi.testclient import TestClient


def test_get_home_message(client: TestClient) -> None:
    """GET /admin/home 이 CommonResponse 포맷으로 Hello Atlas를 반환하는지 확인."""
    response = client.get("/admin/home")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["message"] == "OK"
    assert data["data"] == {"message": "Hello Atlas"}
