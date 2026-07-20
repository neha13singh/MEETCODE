from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

connect_args = {}
db_uri = str(settings.SQLALCHEMY_DATABASE_URI)
if "localhost" not in db_uri and "127.0.0.1" not in db_uri and "db" not in db_uri:
    connect_args["ssl"] = True

engine = create_async_engine(
    db_uri,
    future=True,
    echo=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
