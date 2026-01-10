"""
Quick update of Dynamics 365 credentials
Usage: python scripts/quick_update_creds.py <client_id> <tenant_id> <client_secret>
"""
import asyncio
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

sys.path.append('.')
from backend.models.client import Client

async def update_credentials(client_id: str, tenant_id: str, client_secret: str):
    engine = create_async_engine('sqlite+aiosqlite:///./farm_data.db', echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(
            select(Client).where(Client.name == "Demo Farm")
        )
        client = result.scalar_one_or_none()

        if not client:
            print("ERROR: Demo client not found!")
            return

        client.dynamics_client_id = client_id
        client.dynamics_tenant_id = tenant_id
        client.dynamics_client_secret = client_secret

        await session.commit()

        print("="*70)
        print("SUCCESS: Dynamics 365 credentials updated!")
        print("="*70)
        print(f"\nClient ID: {client_id[:20]}...")
        print(f"Tenant ID: {tenant_id[:20]}...")
        print(f"Secret: {client_secret[:20]}...")
        print("\nYour system is now ready to sync with Dynamics 365!")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python scripts/quick_update_creds.py <client_id> <tenant_id> <client_secret>")
        print("\nExample:")
        print('  python scripts/quick_update_creds.py "a1b2c3d4-..." "f9e8d7c6-..." "abc123~XYZ..."')
        sys.exit(1)

    asyncio.run(update_credentials(sys.argv[1], sys.argv[2], sys.argv[3]))
