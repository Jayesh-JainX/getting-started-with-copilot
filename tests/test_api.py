import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Chess Club"
PARTICIPANT_EMAIL = "student@mergington.edu"


@pytest.fixture
def sample_activities(monkeypatch):
    activities = {
        ACTIVITY_NAME: {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(sample_activities):
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client, sample_activities):
    # Arrange
    expected_activities = sample_activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, sample_activities):
    # Arrange
    email = PARTICIPANT_EMAIL

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {ACTIVITY_NAME}"
    }
    assert email in sample_activities[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_participant(client, sample_activities):
    # Arrange
    email = sample_activities[ACTIVITY_NAME]["participants"][0]
    original_participants = list(sample_activities[ACTIVITY_NAME]["participants"])

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"
    assert sample_activities[ACTIVITY_NAME]["participants"] == original_participants


def test_signup_rejects_unknown_activity(client, sample_activities):
    # Arrange
    email = PARTICIPANT_EMAIL
    original_activities = {
        name: dict(details, participants=list(details["participants"]))
        for name, details in sample_activities.items()
    }

    # Act
    response = client.post("/activities/Unknown/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    assert sample_activities == original_activities


def test_remove_participant_unregisters_student(client, sample_activities):
    # Arrange
    email = sample_activities[ACTIVITY_NAME]["participants"][0]

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {ACTIVITY_NAME}"}
    assert email not in sample_activities[ACTIVITY_NAME]["participants"]


def test_remove_participant_rejects_unknown_activity(client, sample_activities):
    # Arrange
    email = PARTICIPANT_EMAIL
    original_activities = {
        name: dict(details, participants=list(details["participants"]))
        for name, details in sample_activities.items()
    }

    # Act
    response = client.delete("/activities/Unknown/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    assert sample_activities == original_activities


def test_remove_participant_rejects_unregistered_student(client, sample_activities):
    # Arrange
    email = PARTICIPANT_EMAIL
    original_participants = list(sample_activities[ACTIVITY_NAME]["participants"])

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up"
    assert sample_activities[ACTIVITY_NAME]["participants"] == original_participants