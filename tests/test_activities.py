from fastapi.testclient import TestClient
from src.app import app
from urllib.parse import quote
import uuid

client = TestClient(app)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    activities = r.json()
    assert isinstance(activities, dict)
    # Some known activity exists
    assert "Chess Club" in activities


def test_signup_and_unregister_flow():
    activity_name = "Chess Club"
    unique_email = f"test+{uuid.uuid4().hex}@example.com"

    # Sign up
    r = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(unique_email)}")
    assert r.status_code == 200
    data = r.json()
    assert "Signed up" in data["message"]

    # Verify participant added
    r = client.get("/activities")
    activities = r.json()
    assert unique_email in activities[activity_name]["participants"]

    # Unregister
    r = client.delete(f"/activities/{quote(activity_name)}/participants?email={quote(unique_email)}")
    assert r.status_code == 200
    data = r.json()
    assert "Unregistered" in data["message"]

    # Verify participant removed
    r = client.get("/activities")
    activities = r.json()
    assert unique_email not in activities[activity_name]["participants"]


def test_unregister_nonexistent_participant():
    activity_name = "Chess Club"
    email = "noone@example.com"

    # Ensure email not present
    r = client.get("/activities")
    activities = r.json()
    if email in activities[activity_name]["participants"]:
        # Remove if present to ensure consistent test conditions
        client.delete(f"/activities/{quote(activity_name)}/participants?email={quote(email)}")

    r = client.delete(f"/activities/{quote(activity_name)}/participants?email={quote(email)}")
    assert r.status_code == 404
    data = r.json()
    assert data["detail"] == "Participant not found"
