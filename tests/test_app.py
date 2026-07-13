from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    activity = activities[activity_name]
    original_participants = list(activity["participants"])

    try:
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        assert response.status_code == 200
        assert email not in activity["participants"]
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
    finally:
        activity["participants"] = original_participants


def test_unregister_participant_returns_404_when_email_is_not_registered():
    response = client.delete("/activities/Chess Club/participants/not-here@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
