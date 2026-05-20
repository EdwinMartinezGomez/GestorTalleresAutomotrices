from collections.abc import Generator
from uuid import uuid4

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def sync_legacy_schema() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("clientes"):
        return

    column_names = {column["name"] for column in inspector.get_columns("clientes")}
    if "id" not in column_names:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE clientes ADD COLUMN id UUID"))

    with engine.begin() as connection:
        clientes_sin_id = connection.execute(text("SELECT documento FROM clientes WHERE id IS NULL")).all()
        for row in clientes_sin_id:
            connection.execute(
                text("UPDATE clientes SET id = :id WHERE documento = :documento"),
                {"id": str(uuid4()), "documento": row.documento},
            )
        connection.execute(text("ALTER TABLE clientes ALTER COLUMN id SET NOT NULL"))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
