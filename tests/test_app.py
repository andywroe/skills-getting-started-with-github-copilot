"""Tests for the Mergington High School API."""

from src.app import activities


# ── GET / ────────────────────────────────────────────────────────────────────

def test_root_redirects(client):
    """GET / should redirect to the static index page."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


# ── GET /activities ──────────────────────────────────────────────────────────

def test_get_activities_returns_all(client):
    """GET /activities should return all activities with expected keys."""
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9

    for name, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


# ── POST /activities/{name}/signup ───────────────────────────────────────────

def test_signup_success(client):
    """Signing up a new student should succeed and add them to participants."""
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_activity_not_found(client):
    """Signing up for a nonexistent activity should return 404."""
    response = client.post("/activities/Nonexistent/signup", params={"email": "a@b.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate(client):
    """Signing up the same student twice should return 400 on the second attempt."""
    email = "duplicate@mergington.edu"
    first = client.post("/activities/Chess Club/signup", params={"email": email})
    assert first.status_code == 200

    second = client.post("/activities/Chess Club/signup", params={"email": email})
    assert second.status_code == 400
    assert "already signed up" in second.json()["detail"].lower()


# ── DELETE /activities/{name}/signup ─────────────────────────────────────────

def test_unregister_success(client):
    """Unregistering an existing participant should succeed and remove them."""
    email = "michael@mergington.edu"
    assert email in activities["Chess Club"]["participants"]

    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found(client):
    """Unregistering from a nonexistent activity should return 404."""
    response = client.delete("/activities/Nonexistent/signup", params={"email": "a@b.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_signed_up(client):
    """Unregistering a student who isn't signed up should return 400."""
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "nobody@mergington.edu"},
    )

    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()
