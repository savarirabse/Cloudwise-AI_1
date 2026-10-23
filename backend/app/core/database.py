from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{settings.DATABASE_USER}:"
    f"{settings.DATABASE_PASSWORD}@"
    f"{settings.DATABASE_HOST}:"
    f"{settings.DATABASE_PORT}/"
    f"{settings.DATABASE_NAME}"
)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
class Base(DeclarativeBase):
    pass
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def test_database_connection():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True