import copy

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def restore_activities_state():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_root_redirects_to_static_index():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_list():
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    json_data = response.json()
    assert "Chess Club" in json_data
    assert "Programming Class" in json_data


def test_signup_for_activity_adds_participant():
    # Arrange
    email = "newstudent@mergington.edu"
    endpoint = "/activities/Chess Club/signup"

    # Act
    response = client.post(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_for_missing_activity_returns_404():
    # Arrange
    endpoint = "/activities/Unknown/signup"

    # Act
    response = client.post(endpoint, params={"email": "newstudent@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_removes_participant():
    # Arrange
    email = "michael@mergington.edu"
    endpoint = "/activities/Chess Club/unregister"

    # Act
    response = client.delete(endpoint, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    endpoint = "/activities/Chess Club/unregister"

    # Act
    response = client.delete(endpoint, params={"email": "missing@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
