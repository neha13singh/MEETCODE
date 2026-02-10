import asyncio
import logging
from app.db.session import engine
from app.db.base_class import Base
from app.models.user import User
from app.models.question import Question, TestCase
from app.models.match import Match, MatchParticipant
from app.models.submission import Submission

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_models():
    async with engine.begin() as conn:
        logger.info("Creating tables...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created successfully")

if __name__ == "__main__":
    asyncio.run(init_models())
