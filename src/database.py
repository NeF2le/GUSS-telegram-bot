from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import settings

engine = create_async_engine(
    url=settings.database_url_asyncpg,
    echo=True
)

SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)
