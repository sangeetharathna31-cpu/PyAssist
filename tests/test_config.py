from pyassist.app.config import Settings


def test_database_config_ignores_replit_managed_database_url(monkeypatch):
    monkeypatch.delenv("PYASSIST_DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://platform-managed.invalid/db")

    assert Settings().DATABASE_URL == "sqlite:///./pyassist.db"

