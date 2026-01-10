"""
Quick script to update Dynamics 365 credentials for demo client
"""
import asyncio
import sys
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

sys.path.append('.')
from backend.models.client import Client

async def update_credentials():
    # Connect to database
    engine = create_async_engine('sqlite+aiosqlite:///./farm_data.db', echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Find the demo client
        result = await session.execute(
            select(Client).where(Client.name == "bioTrack+ Demo")
        )
        client = result.scalar_one_or_none()

        if not client:
            print("ERROR: Demo client not found!")
            return

        print("\nCurrent credentials:")
        print(f"  Client ID: {client.dynamics_client_id}")
        print(f"  Tenant ID: {client.dynamics_tenant_id}")
        print(f"  Secret: {client.dynamics_client_secret[:20]}...")
        print()

        # Get new credentials from user
        print("Enter your Azure AD credentials:")
        print("(Get these from Azure Portal -> App Registrations)")
        print()

        client_id = input("Application (client) ID: ").strip()
        tenant_id = input("Directory (tenant) ID: ").strip()
        client_secret = input("Client Secret: ").strip()

        if not client_id or not tenant_id or not client_secret:
            print("\nERROR: All three values are required!")
            return

        # Update client
        client.dynamics_client_id = client_id
        client.dynamics_tenant_id = tenant_id
        client.dynamics_client_secret = client_secret

        await session.commit()

        print("\n" + "="*70)
        print("SUCCESS: Dynamics 365 credentials updated!")
        print("="*70)
        print("\nYour system is now configured to sync with Dynamics 365!")
        print("Test it by uploading a voice recording about adding an animal.")
        print()

if __name__ == "__main__":
    asyncio.run(update_credentials())
