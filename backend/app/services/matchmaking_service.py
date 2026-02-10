import json
import time
import logging
import random
import string
from typing import Optional, List, Tuple
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.core.config import settings
from app.models.match import Match, MatchParticipant
from app.models.question import Question, TestCase
from app.models.user import User # explicit import
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class MatchmakingService:
    def __init__(self):
        self.redis = redis.from_url(f"redis://{settings.REDIS_HOST}:6379", decode_responses=True)
        self.QUEUE_PREFIX = "matchmaking:queue:"

    async def add_to_queue(self, user_id: str, difficulty: str) -> None:
        """Add user to matchmaking queue with timestamp score"""
        queue_key = f"{self.QUEUE_PREFIX}{difficulty}"
        await self.redis.zadd(queue_key, {user_id: time.time()})
        logger.info(f"User {user_id} added to queue {difficulty}")

    async def remove_from_queue(self, user_id: str, difficulty: str) -> None:
        """Remove user from queue"""
        queue_key = f"{self.QUEUE_PREFIX}{difficulty}"
        await self.redis.zrem(queue_key, user_id)
        logger.info(f"User {user_id} removed from queue {difficulty}")

    async def check_queue(self, difficulty: str, db: AsyncSession) -> Optional[Tuple[str, str, str]]:
        """
        Check if queue has enough players for a match.
        Returns: (match_id, user1_id, user2_id) if match created, else None
        """
        queue_key = f"{self.QUEUE_PREFIX}{difficulty}"
        
        # Check active count
        count = await self.redis.zcard(queue_key)
        
        if count >= 2:
            # Pop 2 oldest users
            # ZPOPMIN returns list of (member, score) tuples
            users_with_scores = await self.redis.zpopmin(queue_key, 2)
            if len(users_with_scores) < 2:
                # Race condition, put back if only 1
                if users_with_scores:
                    await self.redis.zadd(queue_key, {users_with_scores[0][0]: users_with_scores[0][1]})
                return None
                
            user1_id = users_with_scores[0][0]
            user2_id = users_with_scores[1][0]
            
            # Create Match in DB
            match_id = await self._create_match(db, user1_id, user2_id, difficulty)
            
            return match_id, user1_id, user2_id
            
        return None

    async def _create_match(self, db: AsyncSession, user1_id: str, user2_id: str, difficulty: str) -> str:
        """Create match record in database"""
        
        # 1. Select a random question of given difficulty
        # Use func.random() for PostgreSQL
        query = select(Question).where(Question.difficulty == difficulty).order_by(func.random()).limit(1)
        result = await db.execute(query)
        question = result.scalars().first()
        
        if not question:
            # Fallback if no specific difficulty found, get any question
            logger.warning(f"No questions found for difficulty {difficulty}, picking random")
            result = await db.execute(select(Question).order_by(func.random()).limit(1))
            question = result.scalars().first()
            if not question:
                raise Exception("No questions available in database")
        
        # 2. Create Match
        # Competitive match time based on difficulty
        # Easy: 30 mins (1800s), Medium: 40 mins (2400s), Hard: 50 mins (3000s)
        time_map = {
            "easy": 1800,
            "medium": 2400,
            "hard": 3000
        }
        max_time = time_map.get(difficulty.lower(), 2400) # Default to 40m if unknown
        
        match = Match(
            question_id=question.id,
            mode="competitive",
            difficulty=difficulty,
            max_time=max_time,
            status="active", # Should start as 'active' or 'waiting'? Let's say active immediately for now
            started_at=datetime.now(timezone.utc)
        )
        db.add(match)
        await db.flush() # get ID
        
        # 3. Add Participants
        p1 = MatchParticipant(match_id=match.id, user_id=uuid.UUID(user1_id))
        p2 = MatchParticipant(match_id=match.id, user_id=uuid.UUID(user2_id))
        
        db.add(p1)
        db.add(p2)
        
        await db.commit()
        await db.refresh(match)
        
        return str(match.id)

    async def create_private_match(self, db: AsyncSession, user_id: str, difficulty: str) -> Tuple[str, str]:
        """
        Create a private match and return (match_id, code).
        """
        # Generate 6-char code
        chars = string.ascii_uppercase + string.digits
        code = ''.join(random.choices(chars, k=6))
        
        # Ensure code uniqueness (simple check)
        while await self.redis.exists(f"private_match:{code}"):
            code = ''.join(random.choices(chars, k=6))
            
        # Create match in DB
        # 1. Select random question
        query = select(Question).where(Question.difficulty == difficulty).order_by(func.random()).limit(1)
        result = await db.execute(query)
        question = result.scalars().first()
        
        if not question:
             # Fallback
            result = await db.execute(select(Question).order_by(func.random()).limit(1))
            question = result.scalars().first()
            
        # 2. Create Match
        # Private match time based on difficulty
        time_map = {
            "easy": 1800,
            "medium": 2400,
            "hard": 3000
        }
        max_time = time_map.get(difficulty.lower(), 2400) # Default 40 mins
        
        match = Match(
            question_id=question.id,
            mode="private",
            difficulty=difficulty,
            max_time=max_time,
            status="waiting", # Waiting for second player
            started_at=datetime.now(timezone.utc)
        )
        db.add(match)
        await db.flush()
        
        # 3. Add Creator as Participant
        p1 = MatchParticipant(match_id=match.id, user_id=uuid.UUID(user_id))
        db.add(p1)
        
        await db.commit()
        await db.refresh(match)
        
        match_id = str(match.id)
        
        # Store in Redis: code -> match_id
        # Expire in 10 minutes if not joined
        await self.redis.setex(f"private_match:{code}", 600, match_id)
        
        return match_id, code

    async def join_private_match(self, db: AsyncSession, user_id: str, code: str) -> Optional[Tuple[str, str, str]]:
        """
        Join a private match using a code.
        Returns: (match_id, owner_id, joiner_id) or None if failed.
        """
        match_id = await self.redis.get(f"private_match:{code}")
        if not match_id:
            return None
            
        # Fetch match to verify and get owner
        query = (
            select(Match)
            .where(Match.id == match_id)
            .options(selectinload(Match.participants))
        )
        result = await db.execute(query)
        match = result.scalars().first()
        
        if not match:
            return None
            
        if match.status != "waiting":
            return None # Already started or finished
            
        # Check if already in match (re-joining?)
        for p in match.participants:
            if str(p.user_id) == user_id:
                return None # Already joined
                
        # Add Joiner
        p2 = MatchParticipant(match_id=match.id, user_id=uuid.UUID(user_id))
        db.add(p2)
        
        # Update status to active
        match.status = "active"
        match.started_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        # Get owner ID
        owner_id = str(match.participants[0].user_id) # First participant is owner
        
        # Remove code from Redis so no one else can join
        await self.redis.delete(f"private_match:{code}")
        
        return str(match.id), owner_id, user_id

matchmaking_service = MatchmakingService()
