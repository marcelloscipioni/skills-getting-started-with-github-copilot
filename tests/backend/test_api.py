from copy import deepcopy

import httpx
import pytest
import pytest_asyncio

from src.app import activities, app


@pytest_asyncio.fixture()
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def restore_activity_state():
    original_state = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original_state))


@pytest.mark.asyncio
async def test_root_redirects_to_static_index_page(client):
    response = await client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


@pytest.mark.asyncio
async def test_get_activities_returns_activity_catalog(client):
    response = await client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


@pytest.mark.asyncio
async def test_signup_for_activity_adds_student_to_participants(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = await client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


@pytest.mark.asyncio
async def test_signup_for_activity_returns_400_for_duplicate_registration(client):
    response = await client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


@pytest.mark.asyncio
async def test_unregister_participant_returns_404_for_missing_activity(client):
    response = await client.delete(
        "/activities/Unknown Club/participants/not-here@example.com"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
