import httpx
import pytest
import pytest_asyncio

from src.app import app, activities


@pytest_asyncio.fixture()
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_unregister_participant_removes_email_from_activity(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    activity = activities[activity_name]
    original_participants = list(activity["participants"])

    try:
        response = await client.delete(f"/activities/{activity_name}/participants/{email}")

        assert response.status_code == 200
        assert email not in activity["participants"]
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
    finally:
        activity["participants"] = original_participants


@pytest.mark.asyncio
async def test_unregister_participant_returns_404_when_email_is_not_registered(client):
    response = await client.delete("/activities/Chess Club/participants/not-here@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
