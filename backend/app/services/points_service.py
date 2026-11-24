"""Point awarding rules for MeetCode.

Rules:
- Every competitive/private match win: +50 points.
- First accepted submission of a question in practice mode: +5 points.

Awards are written to ``point_awards`` first. The unique constraint on
(user_id, reason, reference_id) makes repeated submissions and duplicate win
events harmless, while the ledger keeps a history for the profile/debug.
"""

import logging
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.point_award import PointAward
from app.models.user import User

logger = logging.getLogger(__name__)

MATCH_WIN_POINTS = 50
PRACTICE_SOLVE_POINTS = 5

REASON_MATCH_WIN = "match_win"
REASON_PRACTICE_SOLVE = "practice_solve"


async def award_points(
    db: AsyncSession,
    *,
    user_id: UUID,
    reason: str,
    reference_id: UUID,
    amount: int,
) -> int:
    """Award points once and return the amount actually granted.

    Returns 0 when this award already exists. Callers must not have any other
    uncommitted changes, because this function commits the ledger entry and
    the user total together.
    """
    stmt = (
        insert(PointAward)
        .values(
            user_id=user_id,
            amount=amount,
            reason=reason,
            reference_id=reference_id,
        )
        .on_conflict_do_nothing(
            index_elements=["user_id", "reason", "reference_id"]
        )
        .returning(PointAward.id)
    )

    result = await db.execute(stmt)
    if result.scalar_one_or_none() is None:
        return 0

    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(points=User.points + amount)
    )
    await db.commit()
    logger.info("Awarded %s points to user %s (%s)", amount, user_id, reason)
    return amount


async def award_match_win(db: AsyncSession, user_id: UUID, match_id: UUID) -> int:
    return await award_points(
        db,
        user_id=user_id,
        reason=REASON_MATCH_WIN,
        reference_id=match_id,
        amount=MATCH_WIN_POINTS,
    )


async def award_practice_solve(db: AsyncSession, user_id: UUID, question_id: UUID) -> int:
    return await award_points(
        db,
        user_id=user_id,
        reason=REASON_PRACTICE_SOLVE,
        reference_id=question_id,
        amount=PRACTICE_SOLVE_POINTS,
    )
