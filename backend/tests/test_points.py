"""End-to-end checks for the points feature.

Run inside a container with a scratch PostgreSQL database:

    TEST_DB_URI=postgresql+asyncpg://user:pass@host:5432/db python tests/test_points.py

The code sandbox is stubbed so the checks are deterministic and do not need
Docker-in-Docker.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

import httpx
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.submissions import execution_service
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.match import Match, MatchParticipant
from app.models.question import Question, TestCase

TEST_DB_URI = os.environ["TEST_DB_URI"]
CHECKED = 0


def check(condition, message):
    global CHECKED
    if not condition:
        raise AssertionError(message)
    CHECKED += 1
    print(f"  PASS: {message}")


async def fake_execute_code(*, code, language, test_cases):
    return [
        {"passed": True, "execution_time": 1, "output": "1"}
        for _ in test_cases
    ]


async def main():
    execution_service.execute_code = fake_execute_code

    engine = create_async_engine(TEST_DB_URI)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    test_session = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with test_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # --- Users -------------------------------------------------------
        alice = (
            await client.post(
                "/api/v1/users/register",
                json={
                    "username": f"alice{uuid4().hex[:6]}",
                    "email": f"alice{uuid4().hex[:6]}@example.com",
                    "password": "secret123",
                },
            )
        ).json()
        bob = (
            await client.post(
                "/api/v1/users/register",
                json={
                    "username": f"bob{uuid4().hex[:6]}",
                    "email": f"bob{uuid4().hex[:6]}@example.com",
                    "password": "secret123",
                },
            )
        ).json()
        check(alice["points"] == 0 and bob["points"] == 0, "new users start at 0 points")

        async def token_for(username, password="secret123"):
            response = await client.post(
                "/api/v1/auth/login",
                data={"username": username, "password": password},
            )
            return response.json()["access_token"]

        def auth(token):
            return {"Authorization": f"Bearer {token}"}

        alice_token = await token_for(alice["username"])
        bob_token = await token_for(bob["username"])

        async def points_for(token):
            return (await client.get("/api/v1/auth/me", headers=auth(token))).json()["points"]

        # --- Question ----------------------------------------------------
        async with test_session() as db:
            question = Question(
                title="Points Test",
                slug=f"points-test-{uuid4().hex[:8]}",
                description="Return 1",
                difficulty="easy",
                avg_solve_time=60,
                test_cases=[
                    TestCase(input="x = 1", expected_output="1", is_sample=True)
                ],
            )
            db.add(question)
            await db.commit()
            await db.refresh(question)
        qid = str(question.id)

        async def submit(token, match_id=None):
            payload = {
                "code": "def solve():\n    return 1\n",
                "language": "python",
                "question_id": qid,
            }
            if match_id:
                payload["match_id"] = match_id
            response = await client.post(
                "/api/v1/submissions/submit", json=payload, headers=auth(token)
            )
            assert response.status_code == 200, response.text
            return response.json()

        async def new_match(mode, user_ids):
            match = Match(
                question_id=question.id,
                mode=mode,
                difficulty="easy",
                max_time=1800,
                status="active",
                started_at=datetime.now(timezone.utc),
            )
            async with test_session() as db:
                db.add(match)
                await db.flush()
                for user_id in user_ids:
                    db.add(MatchParticipant(match_id=match.id, user_id=user_id))
                await db.commit()
                return str(match.id)

        # --- Practice: +5 once -------------------------------------------
        practice = (
            await client.post(
                "/api/v1/matches/",
                json={"mode": "practice", "question_id": qid},
                headers=auth(alice_token),
            )
        ).json()
        first = await submit(alice_token, practice["id"])
        check(first["points_awarded"] == 5, "first practice solve awards +5")
        check(await points_for(alice_token) == 5, "user total is 5 after first practice solve")

        practice_again = (
            await client.post(
                "/api/v1/matches/",
                json={"mode": "practice", "question_id": qid},
                headers=auth(alice_token),
            )
        ).json()
        repeat = await submit(alice_token, practice_again["id"])
        check(repeat["points_awarded"] == 0, "re-solving the same question awards 0")
        check(await points_for(alice_token) == 5, "points stay at 5 after a repeat solve")

        # --- Competitive win: +50 once ----------------------------------
        comp = await new_match("competitive", [alice["id"], bob["id"]])
        win = await submit(alice_token, comp)
        check(win["points_awarded"] == 50, "competitive win awards +50")
        check(await points_for(alice_token) == 55, "user total is 55 after a win")

        duplicate = await submit(alice_token, comp)
        check(duplicate["points_awarded"] == 0, "duplicate win submission awards 0")
        check(await points_for(alice_token) == 55, "points stay at 55 after duplicate win")

        # --- Win by surrender: +50 ---------------------------------------
        comp2 = await new_match("competitive", [alice["id"], bob["id"]])
        surrendered = await client.post(
            f"/api/v1/matches/{comp2}/surrender", headers=auth(bob_token)
        )
        check(surrendered.status_code == 200, "surrender succeeds")
        check(surrendered.json()["points_awarded"] == 50, "surrender awards winner +50")
        check(await points_for(alice_token) == 105, "winner total is 105 after surrender")
        check(await points_for(bob_token) == 0, "surrendering user gets no points")

        # --- API exposure -------------------------------------------------
        me = (await client.get("/api/v1/users/me", headers=auth(alice_token))).json()
        check(me["points"] == 105, "/users/me exposes the points total")

    await engine.dispose()
    print(f"\nAll {CHECKED} point checks passed.")


if __name__ == "__main__":
    asyncio.run(main())
