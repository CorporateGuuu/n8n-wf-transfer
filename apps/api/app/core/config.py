from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite+pysqlite:///./ops_intelligence.db")
    token_secret: str = os.getenv("TOKEN_SECRET", "local-development-only-change-me")
    access_token_ttl_seconds: int = int(os.getenv("ACCESS_TOKEN_TTL_SECONDS", "900"))
    refresh_token_ttl_seconds: int = int(os.getenv("REFRESH_TOKEN_TTL_SECONDS", str(30 * 24 * 3600)))

    def __post_init__(self) -> None:
        if self.app_env.strip().lower() not in {"development", "test", "testing"}:
            if (
                self.token_secret == "local-development-only-change-me"
                or len(self.token_secret.encode("utf-8")) < 32
            ):
                raise ValueError("Non-development environments require an explicit signing secret of at least 32 bytes")


settings = Settings()
