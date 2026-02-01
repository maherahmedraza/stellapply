import pytest
from httpx import AsyncClient


class TestPersonaEndpoints:
    @pytest.mark.asyncio
    async def test_create_persona(self, auth_client: AsyncClient):
        response = await auth_client.post(
            "/api/v1/persona",
            json={
                "full_name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "location": {"city": "San Francisco", "state": "CA", "country": "USA"},
                "work_authorization": "citizen",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "John Doe"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_persona(self, auth_client: AsyncClient, test_persona):
        response = await auth_client.get("/api/v1/persona")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_persona["id"]

    @pytest.mark.asyncio
    async def test_update_persona(self, auth_client: AsyncClient, test_persona):
        response = await auth_client.put(
            "/api/v1/persona", json={"full_name": "Jane Doe"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Jane Doe"

    @pytest.mark.asyncio
    async def test_add_experience(self, auth_client: AsyncClient, test_persona):
        response = await auth_client.post(
            "/api/v1/persona/experiences",
            json={
                "company": "Tech Corp",
                "title": "Software Engineer",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "description": "Built awesome software",
                "achievements": [
                    "Led team of 5 engineers",
                    "Shipped 10 major features",
                ],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["company"] == "Tech Corp"
        assert len(data["achievements"]) == 2

    @pytest.mark.asyncio
    async def test_get_completeness_score(self, auth_client: AsyncClient, test_persona):
        response = await auth_client.get("/api/v1/persona/completeness")

        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert 0 <= data["score"] <= 100
        assert "suggestions" in data

    @pytest.mark.asyncio
    async def test_export_persona_gdpr(self, auth_client: AsyncClient, test_persona):
        response = await auth_client.get("/api/v1/persona/export")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert "persona" in data
        assert "experiences" in data
        assert "skills" in data

    @pytest.mark.asyncio
    async def test_unauthorized_access_rejected(self, client: AsyncClient):
        response = await client.get("/api/v1/persona")

        assert response.status_code == 401
