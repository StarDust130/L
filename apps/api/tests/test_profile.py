from apps.api.app.core.auth import require_user
from app.main import app
from apps.api.app.profile.schemas.profile import CandidateProfile
from fastapi.testclient import TestClient


def example_profile() -> dict:
    return {
        "full_name": "Aman Sharma",
        "target_roles": ["Python Developer"],
        "skills": ["Python", "FastAPI"],
        "experience": ["Built an API project"],
        "education": ["B.Tech Computer Science"],
        "locations": ["India"],
        "remote_preference": "remote",
        "years_of_experience": 1,
        "work_authorization": "India",
        "links": ["https://github.com/example"],
    }


def test_profile_save_and_read() -> None:
    test_user_id = "test_profile_user"

    # 🔐 Fake authentication for this test
    app.dependency_overrides[require_user] = lambda: test_user_id

    try:
        with TestClient(app) as client:
            save_response = client.put(
                "/api/profile",
                json=example_profile(),
            )

            assert save_response.status_code == 200
            assert save_response.json()["full_name"] == "Aman Sharma"

            read_response = client.get("/api/profile")

            assert read_response.status_code == 200
            assert read_response.json()["target_roles"] == ["Python Developer"]

    finally:
        # 🧹 Remove the fake authentication after the test
        app.dependency_overrides.clear()


def test_profile_schema_rejects_unknown_fields() -> None:
    profile = example_profile()
    profile["unknown_field"] = "not allowed"

    try:
        CandidateProfile.model_validate(profile)
        assert False
    except ValueError:
        assert True
