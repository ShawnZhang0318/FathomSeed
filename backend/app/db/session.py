import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base


BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_STORAGE_DIR = BACKEND_ROOT / "storage"


def _default_storage_dir() -> Path:
    configured = os.getenv("FULLMIND_STORAGE_DIR")
    if configured:
        configured_path = Path(configured).expanduser().resolve()
        try:
            configured_path.relative_to(BACKEND_ROOT)
        except ValueError as exc:
            raise ValueError("FULLMIND_STORAGE_DIR must stay inside the backend project directory.") from exc
        return configured_path

    return PROJECT_STORAGE_DIR


DEFAULT_DB_FILENAME = os.getenv("FULLMIND_DB_FILENAME", "fullmind_app.db")
DEFAULT_DB_PATH = _default_storage_dir() / DEFAULT_DB_FILENAME
DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")
SQLITE_JOURNAL_MODE = os.getenv("FULLMIND_SQLITE_JOURNAL_MODE", "OFF").upper()

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute(f"PRAGMA journal_mode={SQLITE_JOURNAL_MODE}")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def init_db() -> None:
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_sqlite_columns()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_sqlite_columns() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    if "learning_plans" not in existing_tables or "plan_tasks" not in existing_tables:
        return

    plan_columns = {column["name"] for column in inspector.get_columns("learning_plans")}
    task_columns = {column["name"] for column in inspector.get_columns("plan_tasks")}
    statements: list[str] = []
    if "experience_policy" not in plan_columns:
        statements.append("ALTER TABLE learning_plans ADD COLUMN experience_policy VARCHAR(48) NOT NULL DEFAULT 'mixed'")
    if "experience_mix" not in plan_columns:
        statements.append("ALTER TABLE learning_plans ADD COLUMN experience_mix JSON NOT NULL DEFAULT '{}'")
    if "experience_mode" not in task_columns:
        statements.append("ALTER TABLE plan_tasks ADD COLUMN experience_mode VARCHAR(48) NOT NULL DEFAULT 'drill'")
    if "content_format" not in task_columns:
        statements.append("ALTER TABLE plan_tasks ADD COLUMN content_format VARCHAR(48) NOT NULL DEFAULT 'exercise'")
    if "progress_percent" not in task_columns:
        statements.append("ALTER TABLE plan_tasks ADD COLUMN progress_percent INTEGER NOT NULL DEFAULT 0")

    if not statements:
        return
    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
