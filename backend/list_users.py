import asyncio
import os
import sys

# Ensure app can be imported
sys.path.append(os.getcwd())

from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def list_users():
    async with AsyncSessionLocal() as db:
        res = await db.execute(text("SELECT username, email FROM users"))
        users = res.all()
        for user in users:
            print(f"Username: {user.username}, Email: {user.email}")

if __name__ == "__main__":
    asyncio.run(list_users())
