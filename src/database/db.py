from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from settings import settings

engine = create_async_engine(settings.get_uri())
async_session_factory = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
async def get_db():
    async with async_session_factory() as session:
        yield session
