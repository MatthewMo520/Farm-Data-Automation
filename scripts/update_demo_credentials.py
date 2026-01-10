"""
Update existing demo client with real bioTrack+ credentials
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.database import AsyncSessionLocal, init_db
from backend.models.client import Client
from sqlalchemy import select


async def update_demo_credentials():
    """Update demo client with real credentials"""

    await init_db()

    async with AsyncSessionLocal() as db:
        # Find existing demo client
        result = await db.execute(select(Client).where(Client.name == "Demo Farm"))
        client = result.scalar_one_or_none()

        if not client:
            print("[ERROR] Demo Farm client not found!")
            return

        # Update with real credentials
        client.name = "bioTrack+ Demo"
        client.dynamics_url = "https://agsights.crm3.dynamics.com"
        client.dynamics_client_id = "demo@biotrack.ca"
        client.dynamics_client_secret = "bioTrack+test"
        client.dynamics_tenant_id = "biotrack-demo"
        client.settings = {
            "username": "demo@biotrack.ca",
            "password": "bioTrack+test",
            "login_url": "https://agsights.crm3.dynamics.com/"
        }

        await db.commit()

        print("\n" + "="*60)
        print("SUCCESS: Demo client updated with real credentials!")
        print("="*60)
        print(f"\nClient Details:")
        print(f"  Name: {client.name}")
        print(f"  ID: {client.id}")
        print(f"  Dynamics URL: {client.dynamics_url}")
        print(f"  Username: demo@biotrack.ca")
        print(f"  Password: bioTrack+test")
        print("\nYou can now login with these credentials in the dashboard!")
        print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(update_demo_credentials())
