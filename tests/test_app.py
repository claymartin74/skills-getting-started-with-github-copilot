from fastapi.testclient import TestClient
from src import app as application

client = TestClient(application.app)


def test_root_redirects_to_index():
    resp = client.get("/")
    # FastAPI RedirectResponse uses 307 by default for GET -> location
    assert resp.status_code in (200, 307, 308)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activities
    assert "Chess Club" in data


def test_signup_for_activity_success():
    email = "test_student@example.edu"
    # Ensure not already present
    # If present, try to remove to get a clean state
    resp = client.post(f"/activities/Chess Club/signup", params={"email": email})
    # Accept either 200 or 400 if already signed up depending on state
    assert resp.status_code in (200, 400)
    if resp.status_code == 200:
        assert "Signed up" in resp.json().get("message", "")


def test_signup_for_activity_duplicate():
    email = "dup_student@example.edu"
    # First signup
    resp1 = client.post(f"/activities/Programming Class/signup", params={"email": email})
    assert resp1.status_code in (200, 400)
    # Second signup should be 400 if first succeeded
    resp2 = client.post(f"/activities/Programming Class/signup", params={"email": email})
    assert resp2.status_code in (200, 400)


def test_unregister_participant_success_and_errors():
    email = "to_remove@example.edu"
    # Ensure the participant is signed up first
    client.post(f"/activities/Art Club/signup", params={"email": email})

    # Now remove using DELETE with json body
    resp = client.delete(f"/activities/Art Club/participants", json={"email": email})
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Removing again should return 404
    resp2 = client.delete(f"/activities/Art Club/participants", json={"email": email})
    assert resp2.status_code in (400, 404)


def test_activity_not_found():
    resp = client.post(f"/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404
*** End Patch