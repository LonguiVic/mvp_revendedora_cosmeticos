from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config.settings import settings

engine = create_async_engine(
    settings.database_url,
    echo=True
)

SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()