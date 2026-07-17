from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from jose import jwt, JWTError
import json
import logging
import asyncio
import time
import uuid
from typing import Dict

from app.core.config import settings
from app.db.session import get_db, AsyncSessionLocal
from app.services.websocket_manager import manager
from app.services.matchmaking_service import matchmaking_service
from app.models.user import User
from app.models.match import Match, MatchParticipant
from app.models.question import Question, TestCase
from app.api import deps
from sqlalchemy import select, func
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Track timeout tasks: user_id -> Task
queue_timeout_tasks: Dict[str, asyncio.Task] = {}

router = APIRouter()

async def handle_queue_timeout(user_id: str, difficulty: str):
    try:
        await asyncio.sleep(60)
        # Timeout reached: remove from queue and notify
        await matchmaking_service.remove_from_queue(user_id, difficulty)
        
        # Cleanup task reference
        if user_id in queue_timeout_tasks:
            del queue_timeout_tasks[user_id]
            
        # Create a real practice match in the database
        async with AsyncSessionLocal() as db:
            # 1. Pick a random question
            query = select(Question).where(Question.difficulty == difficulty).order_by(func.random()).limit(1)
            result = await db.execute(query)
            question = result.scalars().first()
            
            if not question:
                result = await db.execute(select(Question).order_by(func.random()).limit(1))
                question = result.scalars().first()
            
            # 2. Create Match
            match = Match(
                question_id=question.id,
                mode="practice",
                difficulty=difficulty,
                max_time=3600, # 1 hour for practice
                status="active",
                started_at=datetime.now(timezone.utc)
            )
            db.add(match)
            await db.flush()
            
            # 3. Add Participant
            participant = MatchParticipant(
                match_id=match.id,
                user_id=uuid.UUID(user_id)
            )
            db.add(participant)
            await db.commit()
            
            # 4. Notify user
            await manager.send_personal_message(
                {"event": "match:practice", "data": {"difficulty": difficulty, "practiceId": str(match.id)}},
                user_id
            )
            # Add to connection groups
            await manager.add_user_to_match(str(match.id), user_id)

    except asyncio.CancelledError:
        # Task was cancelled (match found or user left), do nothing
        pass
    except Exception as e:
        logger.error(f"Error in handle_queue_timeout: {e}")

async def get_user_from_token(token: str, db: AsyncSession) -> User:
    try:
        logger.info(f"Decoding WebSocket token: {token[:15]}... with secret: {settings.SECRET_KEY[:3]}...")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token payload lacks 'sub' claim")
            return None
    except JWTError as e:
        logger.warning(f"JWT decode failed: {e}")
        return None
        
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
         logger.warning(f"User '{username}' not found in database")
    return user

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str, # passed as query param ?token=...
    db: AsyncSession = Depends(get_db)
):
    # Accept connection first so we can log errors and return descriptive codes/messages
    await websocket.accept()
    
    # Verify User
    user = await get_user_from_token(token, db)
    if not user:
        logger.warning(f"Authentication failed for WebSocket client.")
        try:
            await websocket.send_json({"event": "auth:error", "data": {"message": "Invalid token or user not found"}})
        except Exception:
            pass
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = str(user.id)
    await manager.connect(websocket, user_id, accept=False)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                event = message.get("event")
                payload = message.get("data", {})
                
                # --- EVENT HANDLERS ---
                
                # 1. Matchmaking: Join Queue
                if event == "queue:join":
                    difficulty = payload.get("difficulty", "medium")  # default to medium
                    await matchmaking_service.add_to_queue(user_id, difficulty)

                    # Start timeout task (cancel existing if any)
                    if user_id in queue_timeout_tasks:
                        queue_timeout_tasks[user_id].cancel()
                    
                    queue_timeout_tasks[user_id] = asyncio.create_task(
                        handle_queue_timeout(user_id, difficulty)
                    )
                    
                    # Notify user they joined
                    await manager.send_personal_message(
                        {"event": "queue:status", "data": {"status": "joined", "difficulty": difficulty}},
                        user_id
                    )
                    
                    # Try to match immediately
                    match_result = await matchmaking_service.check_queue(difficulty, db)
                    
                    if match_result:
                        match_id, p1_id, p2_id = match_result
                        
                        # Cancel timeout tasks for both users
                        for pid in [p1_id, p2_id]:
                            if pid in queue_timeout_tasks:
                                queue_timeout_tasks[pid].cancel()
                                del queue_timeout_tasks[pid]
                        
                        start_time = int(time.time() * 1000) + 5000  # Start in 5 seconds

                        
                        # Notify P1
                        await manager.send_personal_message(
                            {"event": "match:found", "data": {"matchId": match_id, "opponentId": p2_id, "startTime": start_time}},
                            p1_id
                        )
                        # Notify P2
                        await manager.send_personal_message(
                            {"event": "match:found", "data": {"matchId": match_id, "opponentId": p1_id, "startTime": start_time}},
                            p2_id
                        )
                        
                        # Add to connection groups
                        await manager.add_user_to_match(match_id, p1_id)
                        await manager.add_user_to_match(match_id, p2_id)

                # 2. Matchmaking: Leave Queue
                elif event == "queue:leave":
                    difficulty = payload.get("difficulty", "medium")
                    
                    # Cancel timeout task
                    if user_id in queue_timeout_tasks:
                        queue_timeout_tasks[user_id].cancel()
                        del queue_timeout_tasks[user_id]

                    await matchmaking_service.remove_from_queue(user_id, difficulty)
                    await manager.send_personal_message(
                        {"event": "queue:status", "data": {"status": "left"}},
                        user_id
                    )

                # 3. Match: Join (User enters the editor page)
                elif event == "match:join":
                    match_id = payload.get("matchId")
                    if match_id:
                        if isinstance(match_id, list):
                            match_id = match_id[0]
                        match_id = str(match_id)
                        await manager.add_user_to_match(match_id, user_id)
                        
                        # Phase 6: Immediate result for late-joiners
                        from app.models.match import Match
                        from sqlalchemy import select
                        match_query = select(Match).where(Match.id == match_id)
                        match_res = await db.execute(match_query)
                        match = match_res.scalars().first()
                        
                        if match and match.status == "completed":
                            await manager.send_personal_message({
                                "event": "match:completed",
                                "data": {
                                    "winnerId": str(match.winner_id) if match.winner_id else None,
                                    "result": "completed",
                                    "reason": "already_finished"
                                }
                            }, user_id)
                
                # 4. Match: Code Update (optional, for collaborative feel or anti-cheat)
                # elif event == "code:update": ...

                # 5. Private Match: Create
                elif event == "match:create_private":
                    difficulty = payload.get("difficulty", "medium")
                    match_id, code = await matchmaking_service.create_private_match(db, user_id, difficulty)
                    
                    # Notify creator with code
                    await manager.send_personal_message(
                        {"event": "match:private_created", "data": {"matchId": match_id, "code": code}},
                        user_id
                    )
                    
                    # Add to match connections so we track them as waiting
                    await manager.add_user_to_match(match_id, user_id)
                    
                # 6. Private Match: Join
                elif event == "match:join_private":
                    code = payload.get("code")
                    result = await matchmaking_service.join_private_match(db, user_id, code)
                    
                    if result:
                        match_id, owner_id, joiner_id = result
                        start_time = int(time.time() * 1000) + 5000 # 5s delay
                        
                        # Notify Owner
                        await manager.send_personal_message(
                            {"event": "match:found", "data": {"matchId": match_id, "opponentId": joiner_id, "startTime": start_time}},
                            owner_id
                        )
                        # Notify Joiner
                        await manager.send_personal_message(
                            {"event": "match:found", "data": {"matchId": match_id, "opponentId": owner_id, "startTime": start_time}},
                            joiner_id
                        )
                        
                        # Add joiner to match connections
                        await manager.add_user_to_match(match_id, joiner_id)
                    else:
                        # Failed to join (invalid code, full, etc.)
                        await manager.send_personal_message(
                            {"event": "match:error", "data": {"message": "Invalid code or match unavailable"}},
                            user_id
                        )

                # 7. Match: Submit Result
                # Done via REST API, but server can push notifications to opponent here
                
                else:
                    logger.warning(f"Unknown event: {event}")

            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
                
    except WebSocketDisconnect:
        # Check if user was in a match before disconnecting
        match_id = manager.user_to_match.get(user_id)
        
        manager.disconnect(user_id)
        
        # Cancel timeout task
        if user_id in queue_timeout_tasks:
            queue_timeout_tasks[user_id].cancel()
            del queue_timeout_tasks[user_id]
            
        # Forfeit logic if in an active competitive match
        if match_id:
            async with AsyncSessionLocal() as db:
                from app.models.match import Match
                match_query = select(Match).where(Match.id == uuid.UUID(match_id)).options(selectinload(Match.participants))
                result = await db.execute(match_query)
                match = result.scalars().first()
                
                if match and match.status == "active" and match.mode == "competitive":
                    # Mark as completed
                    match.status = "completed"
                    match.completed_at = datetime.now(timezone.utc)
                    
                    winner_id = None
                    # Update participants
                    for p in match.participants:
                        if str(p.user_id) == user_id:
                            p.result = "lose"
                        else:
                            p.result = "win"
                            match.winner_id = p.user_id
                            winner_id = str(p.user_id)
                        p.completed_at = datetime.now(timezone.utc)
                        db.add(p)
                    
                    db.add(match)
                    await db.commit()
                    
                    # Notify opponent if they are still connected
                    await manager.broadcast_match_event(
                        match_id=match_id,
                        event_type="match:completed",
                        data={
                            "winnerId": winner_id,
                            "reason": "forfeit",
                            "forfeiterId": user_id
                        }
                    )

        # Handle cleanup: remove from queues if potentially searching
        # await matchmaking_service.remove_from_queue(user_id, "active_difficulty") # need state tracking for this
