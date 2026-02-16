import asyncio
import os
import sys

# Add app directory to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

from sqlalchemy import text
from core.database import AsyncSessionLocal

async def cleanup():
    print("Cleaning up legacy projects with missing properties...")
    async with AsyncSessionLocal() as session:
        # Option 1: Delete all projects (Simplest since data is lost anyway)
        await session.execute(text("DELETE FROM projects"))
        await session.commit()
        print("All projects deleted. Database is clean.")

if __name__ == "__main__":
    asyncio.run(cleanup())
