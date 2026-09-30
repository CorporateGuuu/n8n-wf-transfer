from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings

_hasher = PasswordHasher()
_serializer = URLSafeTimedSerializer(settings.token_secret, salt="ops-intelligence-access")


@dataclass(frozen=True)
class RefreshCredential:
    raw: str
    token_hash: str


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def create_access_token(user_id: str) -> str:
    return _serializer.dumps({"sub": user_id})


def read_access_token(token: str) -> str | None:
    try:
        payload = _serializer.loads(token, max_age=settings.access_token_ttl_seconds)
    except (BadSignature, SignatureExpired):
        return None
    return payload.get("sub")


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_refresh_credential() -> RefreshCredential:
    raw = secrets.token_urlsafe(48)
    return RefreshCredential(raw=raw, token_hash=hash_refresh_token(raw))
