from fastapi.testclient import TestClient
from src import app as application

client = TestClient(application.app)


def test_root_redirects_to_index():
    resp = client.get("/")
    assert resp.status_code in (200, 307, 308)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_cycle():
    email = "cycle_student@example.edu"
    # Signup
    resp = client.post(f"/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code in (200, 400)

    # If signup succeeded, try to unregister
    if resp.status_code == 200:
        resp2 = client.request("DELETE", f"/activities/Chess Club/participants", json={"email": email})
        assert resp2.status_code == 200
        assert "Unregistered" in resp2.json().get("message", "")


def test_activity_not_found():
    resp = client.post(f"/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404
