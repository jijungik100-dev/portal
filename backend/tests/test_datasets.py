from fastapi.testclient import TestClient


class TestListDatasets:
    """GET /api/v1.0/datasets 테스트."""

    def test_empty_list(self, client: TestClient) -> None:
        """데이터셋이 없을 때 빈 리스트를 반환한다."""
        response = client.get("/api/v1.0/datasets")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"] == []

    def test_list_with_data(self, client: TestClient) -> None:
        """데이터셋 생성 후 목록 조회에 포함된다."""
        # 데이터셋 생성
        client.post("/api/v1.0/datasets", json={"name": "test-ds", "source_type": "file"})

        response = client.get("/api/v1.0/datasets")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "test-ds"


class TestCreateDataset:
    """POST /api/v1.0/datasets 테스트."""

    def test_create_success(self, client: TestClient) -> None:
        """데이터셋을 정상 생성한다."""
        payload = {"name": "sales-data", "description": "매출 데이터", "source_type": "database"}
        response = client.post("/api/v1.0/datasets", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "sales-data"
        assert data["data"]["description"] == "매출 데이터"
        assert data["data"]["source_type"] == "database"
        assert data["data"]["is_active"] is True
        assert "id" in data["data"]
        assert "created_at" in data["data"]
        assert "updated_at" in data["data"]

    def test_create_minimal(self, client: TestClient) -> None:
        """필수 필드만으로 데이터셋을 생성한다."""
        payload = {"name": "minimal-ds", "source_type": "api"}
        response = client.post("/api/v1.0/datasets", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["name"] == "minimal-ds"
        assert data["data"]["description"] is None


class TestGetDataset:
    """GET /api/v1.0/datasets/{dataset_id} 테스트."""

    def test_get_existing(self, client: TestClient) -> None:
        """존재하는 데이터셋을 조회한다."""
        # 생성
        create_resp = client.post("/api/v1.0/datasets", json={"name": "get-test", "source_type": "file"})
        dataset_id = create_resp.json()["data"]["id"]

        # 조회
        response = client.get(f"/api/v1.0/datasets/{dataset_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == dataset_id
        assert data["data"]["name"] == "get-test"

    def test_get_not_found(self, client: TestClient) -> None:
        """존재하지 않는 데이터셋 조회 시 404를 반환한다."""
        response = client.get("/api/v1.0/datasets/99999")
        assert response.status_code == 404


class TestUpdateDataset:
    """PUT /api/v1.0/datasets/{dataset_id} 테스트."""

    def test_update_success(self, client: TestClient) -> None:
        """데이터셋을 정상 수정한다."""
        # 생성
        create_resp = client.post("/api/v1.0/datasets", json={"name": "original", "source_type": "file"})
        dataset_id = create_resp.json()["data"]["id"]

        # 수정
        response = client.put(f"/api/v1.0/datasets/{dataset_id}", json={"name": "updated", "is_active": False})
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "updated"
        assert data["data"]["is_active"] is False
        assert data["data"]["source_type"] == "file"  # 변경하지 않은 필드는 유지

    def test_update_not_found(self, client: TestClient) -> None:
        """존재하지 않는 데이터셋 수정 시 404를 반환한다."""
        response = client.put("/api/v1.0/datasets/99999", json={"name": "x"})
        assert response.status_code == 404


class TestDeleteDataset:
    """DELETE /api/v1.0/datasets/{dataset_id} 테스트."""

    def test_delete_success(self, client: TestClient) -> None:
        """데이터셋을 정상 삭제한다."""
        # 생성
        create_resp = client.post("/api/v1.0/datasets", json={"name": "to-delete", "source_type": "file"})
        dataset_id = create_resp.json()["data"]["id"]

        # 삭제
        response = client.delete(f"/api/v1.0/datasets/{dataset_id}")
        assert response.status_code == 204

        # 삭제 확인
        get_resp = client.get(f"/api/v1.0/datasets/{dataset_id}")
        assert get_resp.status_code == 404

    def test_delete_not_found(self, client: TestClient) -> None:
        """존재하지 않는 데이터셋 삭제 시 404를 반환한다."""
        response = client.delete("/api/v1.0/datasets/99999")
        assert response.status_code == 404


class TestCalculateDatasets:
    """POST /api/v1.0/datasets:calculate 테스트."""

    def test_calculate_empty(self, client: TestClient) -> None:
        """데이터셋이 없을 때 모두 0을 반환한다."""
        response = client.post("/api/v1.0/datasets:calculate")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 0
        assert data["data"]["active"] == 0
        assert data["data"]["inactive"] == 0

    def test_calculate_with_data(self, client: TestClient) -> None:
        """데이터셋 생성 후 카운트를 올바르게 계산한다."""
        # active 2개 생성
        client.post("/api/v1.0/datasets", json={"name": "ds-1", "source_type": "file"})
        client.post("/api/v1.0/datasets", json={"name": "ds-2", "source_type": "database"})

        # 1개를 inactive로 수정
        create_resp = client.post("/api/v1.0/datasets", json={"name": "ds-3", "source_type": "api"})
        dataset_id = create_resp.json()["data"]["id"]
        client.put(f"/api/v1.0/datasets/{dataset_id}", json={"is_active": False})

        # calculate
        response = client.post("/api/v1.0/datasets:calculate")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["total"] == 3
        assert data["data"]["active"] == 2
        assert data["data"]["inactive"] == 1
