import pytest
from sqlalchemy import func, select

from app.db.models import RefreshSession, User


@pytest.mark.parametrize("stored_hash", ["", "not-an-argon-hash", "$argon2id$v=19$m=65536,t=3,p=4$broken"])
def test_corrupt_stored_password_fails_closed_without_issuing_session(client, db_session, stored_hash):
    user = db_session.scalar(select(User).where(User.email == "admin@northstar.example"))
    user.password_hash = stored_hash
    db_session.commit()
    response = client.post("/api/v1/auth/login", json={
        "organization_slug":"northstar", "email":"admin@northstar.example", "password":"SyntheticPass123!"
    })
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert body["error"]["message"] == "Invalid credentials"
    assert body["error"]["request_id"] == response.headers["X-Request-ID"]
    assert "password" not in response.text.lower()
    assert db_session.scalar(select(func.count()).select_from(RefreshSession)) == 0


def test_password_verification_runtime_error_fails_closed(monkeypatch):
    from argon2.exceptions import VerificationError
    from app.core import security
    def unavailable_verifier(*args):
        raise VerificationError("synthetic verifier error")
    monkeypatch.setattr(type(security._hasher),"verify",unavailable_verifier)
    assert security.verify_password("synthetic", "synthetic") is False
