import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.core.config import Settings


@pytest.mark.parametrize("environment", ["production", "staging", " Production "])
@pytest.mark.parametrize("secret", ["local-development-only-change-me", "", "short-fixture"])
def test_non_development_rejects_public_default_or_short_secret(environment, secret):
    with pytest.raises(ValueError) as error:
        Settings(app_env=environment, token_secret=secret)
    assert secret not in str(error.value) or secret == ""


def test_development_fixture_remains_explicitly_available():
    assert Settings(app_env="development", token_secret="fixture").app_env == "development"


def test_non_development_accepts_explicit_synthetic_long_secret():
    assert Settings(app_env="production", token_secret="synthetic-test-only-" + "x" * 32).app_env == "production"


@pytest.mark.parametrize("secret,accepted", [(None, False), ("short-fixture", False), ("synthetic-fixture-" + "x" * 32, True)])
def test_actual_settings_import_enforces_production_environment(secret, accepted):
    environment = os.environ.copy()
    environment["APP_ENV"] = "production"
    if secret is None:
        environment.pop("TOKEN_SECRET", None)
    else:
        environment["TOKEN_SECRET"] = secret
    result = subprocess.run(
        [sys.executable, "-c", "from app.core.config import settings"],
        env=environment,
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )
    assert (result.returncode == 0) == accepted
    if not accepted:
        assert "Non-development environments require" in result.stderr
    if secret:
        assert secret not in result.stdout + result.stderr
