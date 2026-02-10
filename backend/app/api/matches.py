from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.db.session import get_db
from app.models.match import Match
from app.models.question import Question
from app.schemas.match import Match as MatchSchema, MatchCreate
import logging
import uuid
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=MatchSchema)
async def create_match(
    *,
    db: AsyncSession = Depends(get_db),
    match_in: MatchCreate,
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new match (practice).
    """
    from app.models.match import Match, MatchParticipant
    from datetime import datetime, timezone
    import uuid
    
    # Defaults
    # Practice match time based on difficulty (if not provided, default to medium/40m)
    # Easy: 30 mins (1800s), Medium: 40 mins (2400s), Hard: 50 mins (3000s)
    
    # Needs to fetch difficulty if not provided in match_in (which it is, usually)
    difficulty = match_in.difficulty or "medium"
    
    time_map = {
        "easy": 1800,
        "medium": 2400,
        "hard": 3000
    }
    max_time = time_map.get(difficulty.lower(), 3600) # Default to 1h if unknown key
    
    # If question_id provided, verify
    if match_in.question_id:
        result = await db.execute(select(Question).where(Question.id == match_in.question_id))
        question = result.scalars().first()
        if not question:
             raise HTTPException(status_code=404, detail="Question not found")
        # Ensure difficulty matches question if not set
        if not match_in.difficulty:
             difficulty = question.difficulty
             max_time = time_map.get(difficulty.lower(), 3600)
             
    # Create Match
    match = Match(
        question_id=match_in.question_id,
        mode=match_in.mode,
        difficulty=difficulty, # Use resolved difficulty
        max_time=max_time,
        status="active",
        started_at=datetime.now(timezone.utc)
    )
    db.add(match)
    await db.flush() # get ID
    
    # Add User as Participant
    participant = MatchParticipant(
        match_id=match.id,
        user_id=current_user.id
    )
    db.add(participant)
    await db.commit()
    await db.refresh(match)
    
    # Eager load for response
    query = (
        select(Match)
        .where(Match.id == match.id)
        .options(
            selectinload(Match.question).selectinload(Question.test_cases),
            selectinload(Match.question).selectinload(Question.templates),
            selectinload(Match.participants)
        )
    )
    result = await db.execute(query)
    return result.scalars().first()

@router.get("/{match_id}", response_model=MatchSchema)
async def read_match(
    match_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Get match by ID with question details.
    """
    try:
        query = (
            select(Match)
            .where(Match.id == match_id)
            .options(
                selectinload(Match.question).selectinload(Question.test_cases),
                selectinload(Match.question).selectinload(Question.templates),
                selectinload(Match.participants)
            )
        )
        result = await db.execute(query)
        match = result.scalars().first()
        
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
            
        # Manually attach timestamp to avoid timezone issues
        # Convert DB datetime to epoch milliseconds
        if match.started_at:
            # Timestamp() returns seconds. *1000 for ms.
            # If naive, assumes local. If aware, uses UTC.
             match_dict = match.__dict__
             # If datetime is naive, force it to be treated as UTC if we know we saved it as UTC?
             # But our last fix used datetime.now() (naive local).
             # So .timestamp() should resolve correctly against system local time.
             match.started_at_ts = match.started_at.timestamp() * 1000
             
        return match
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{match_id}/surrender")
async def surrender_match(
    match_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Surrender a match (Battle Mode).
    """
    from datetime import datetime, timezone
    from app.services.websocket_manager import manager
    
    # Fetch Match
    query = (
        select(Match)
        .where(Match.id == match_id)
        .options(selectinload(Match.participants))
    )
    result = await db.execute(query)
    match = result.scalars().first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    if match.status != "active":
        raise HTTPException(status_code=400, detail=f"Match is not active (status: {match.status})")
        
    # Verify User is Participant
    participant = next((p for p in match.participants if str(p.user_id) == str(current_user.id)), None)
    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant")
        
    # Identify Opponent (assuming 1v1)
    opponent = next((p for p in match.participants if str(p.user_id) != str(current_user.id)), None)
    
    # Update Results
    participant.result = "lose"
    participant.completed_at = datetime.now(timezone.utc)
    
    winner_id = None
    if opponent:
        opponent.result = "win"
        match.winner_id = opponent.user_id
        winner_id = str(opponent.user_id)
    
    match.status = "completed"
    match.completed_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    # Broadcast Completion
    await manager.broadcast_match_event(
        match_id=str(match.id),
        event_type="match:completed",
        data={
            "matchId": str(match.id),
            "winnerId": winner_id,
            "reason": "surrender",
            "surrendererId": str(current_user.id)
        }
    )
    
    return {"status": "surrendered"}

@router.post("/{match_id}/timeout")
async def timeout_match(
    match_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Mark match as timed out.
    """
    from datetime import datetime
    from app.services.websocket_manager import manager
    
    # Fetch Match
    query = (
        select(Match)
        .where(Match.id == match_id)
        .options(selectinload(Match.participants))
    )
    result = await db.execute(query)
    match = result.scalars().first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    if match.status != "active":
        # If already completed or timed out, just return success
        return {"status": "already_completed"}
        
    # Verify User is Participant
    participant = next((p for p in match.participants if str(p.user_id) == str(current_user.id)), None)
    if not participant:
        raise HTTPException(status_code=403, detail="Not a participant")
        
    # Update Status
    # Only update if still active (atomic check not strictly needed for this MVP but good practice)
    if match.status == "active":
        # Determine status: Always set to timeout if explicit timeout endpoint is called
        match.status = "timeout"
        match.completed_at = datetime.utcnow()
        
        # Phase 6 Update: Both people time out in competitive if nobody solved it
        for p in match.participants:
            if p.result != "win":
                p.result = "timeout"
            p.completed_at = datetime.utcnow()
            db.add(p)
        
        await db.commit()
        
        # Broadcast Completion
        await manager.broadcast_match_event(
            match_id=str(match.id),
            event_type="match:completed", 
            data={
                "matchId": str(match.id),
                "winnerId": None,
                "reason": "timeout",
                "result": "timeout"
            }
        )
    
    return {"status": match.status}
    
    return {"status": "timed_out"}
