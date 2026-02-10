from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.submission import Submission
from app.models.question import Question, TestCase
from app.models.user import User
from app.schemas.submission import SubmissionRun, SubmissionCreate, SubmissionResponse, SubmissionResult
from app.db.session import get_db
from app.services.execution_service import ExecutionService
import logging
logger = logging.getLogger(__name__)

router = APIRouter()
execution_service = ExecutionService()

@router.get("/", response_model=List[SubmissionResponse])
async def get_submissions(
    question_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """
    Get submissions for a specific question.
    """
    query = (
        select(Submission)
        .where(
            Submission.user_id == current_user.id,
            Submission.question_id == question_id
        )
        .order_by(Submission.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/run", response_model=SubmissionResult)
async def run_code(
    *,
    db: AsyncSession = Depends(get_db),
    submission_in: SubmissionRun,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Run code against SAMPLE test cases only. Does not save submission to DB.
    """
    # Fetch question and sample test cases
    query = select(Question).where(Question.id == submission_in.question_id).options(
        selectinload(Question.test_cases)
    )
    result = await db.execute(query)
    question = result.scalars().first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    # Filter for sample test cases
    # If no explicitly marked samples, take first 2
    sample_tests = [tc for tc in question.test_cases if tc.is_sample]
    if not sample_tests:
        sample_tests = question.test_cases[:2]
        
    if not sample_tests:
        raise HTTPException(status_code=400, detail="No test cases available for this question")

    # Format test cases for execution
    test_cases_payload = [
        {
            "id": str(tc.id),
            "input": tc.input,
            "expected_output": tc.expected_output
        }
        for tc in sample_tests
    ]
    
    # Execute
    results = await execution_service.execute_code(
        code=submission_in.code,
        language=submission_in.language,
        test_cases=test_cases_payload
    )
    
    # Analyze results
    total = len(results)
    passed = sum(1 for r in results if r.get('passed', False))
    error = next((r.get('error') for r in results if r.get('error')), None)
    
    status_str = "accepted" if passed == total else "wrong_answer"
    if error:
        status_str = "runtime_error" # Simplification
        
    return {
        "status": status_str,
        "test_cases_passed": passed,
        "total_test_cases": total,
        "error_message": error,
        "details": results
    }

@router.post("/submit", response_model=SubmissionResponse)
async def submit_code(
    *,
    db: AsyncSession = Depends(get_db),
    submission_in: SubmissionCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Submit code against ALL test cases. Saves submission.
    """
    # Fetch question and ALL test cases
    query = select(Question).where(Question.id == submission_in.question_id).options(
        selectinload(Question.test_cases)
    )
    result = await db.execute(query)
    question = result.scalars().first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Format test cases
    test_cases_payload = [
        {
            "id": str(tc.id),
            "input": tc.input,
            "expected_output": tc.expected_output
        }
        for tc in question.test_cases
    ]
    
    # Execute
    results = await execution_service.execute_code(
        code=submission_in.code,
        language=submission_in.language,
        test_cases=test_cases_payload
    )
    
    # Analyze results
    total = len(results)
    passed = sum(1 for r in results if r.get('passed', False))
    error = next((r.get('error') for r in results if r.get('error')), None)
    
    avg_time = 0
    times = [r.get('execution_time', 0) for r in results if isinstance(r.get('execution_time'), (int, float))]
    if times:
        avg_time = int(sum(times) / len(times))
        
    status_str = "accepted" if passed == total else "wrong_answer"
    if error:
        status_str = "runtime_error" 
        
    # Save submission
    submission = Submission(
        user_id=current_user.id,
        question_id=question.id,
        code=submission_in.code,
        language=submission_in.language,
        submission_type="submit",
        status=status_str,
        test_cases_passed=passed,
        total_test_cases=total,
        execution_time=avg_time,
        error_message=error,
        match_participant_id=None # For now
    )
    
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    
    # Return response
    resp = SubmissionResponse.from_orm(submission)
    resp.details = results
    
    # Notify Match via WebSocket that a submission occurred
    if submission_in.match_id:
        from app.services.websocket_manager import manager
        
        # Broadcast to match
        await manager.broadcast_match_event(
            match_id=str(submission_in.match_id),
            event_type="match:opponent_submitted",
            data={
                "userId": str(current_user.id),
                "status": status_str,
                "passed": passed,
                "total": total
            }
        )
        
        # If accepted (ALL passed), check if match is active and complete it
        if status_str == "accepted":
            # Fetch match to check status (avoid double win)
            # This should be wrapped in a transaction or lock in real production
            from app.models.match import Match, MatchParticipant
            from datetime import datetime
            
            # Re-fetch match with participants
            match_query = select(Match).where(Match.id == submission_in.match_id).options(selectinload(Match.participants))
            match_res = await db.execute(match_query)
            match = match_res.scalars().first()
            
            if match and match.status == "active":
                # Update Match
                match.status = "completed"
                match.winner_id = current_user.id
                match.completed_at = datetime.utcnow()
                db.add(match)
                
                # Update Participants
                for p in match.participants:
                    if p.user_id == current_user.id:
                        p.result = "win"
                        p.completed_at = datetime.utcnow()
                        p.solution_code = submission_in.code
                        p.test_cases_passed = passed
                        p.total_test_cases = total
                        # p.execution_time = avg_time
                    else:
                        p.result = "lose"
                        p.completed_at = datetime.utcnow() # Technically they finished when match finished
                    db.add(p)
                
                await db.commit()
                
                # Broadcast WINNER!
                await manager.broadcast_match_event(
                    match_id=str(submission_in.match_id),
                    event_type="match:completed",
                    data={
                        "winnerId": str(current_user.id),
                        "result": "win" # This user won
                    }
                )
    
    return resp
