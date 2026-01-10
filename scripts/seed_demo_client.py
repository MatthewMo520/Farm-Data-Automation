"""
Seed script to create demo client and schema mapping for testing
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.database import AsyncSessionLocal, init_db
from backend.models.client import Client
from backend.models.schema_mapping import SchemaMapping


async def seed_demo_client():
    """Create a demo client and bioTrack schema mapping"""

    await init_db()

    async with AsyncSessionLocal() as db:
        # Check if demo client already exists
        from sqlalchemy import select
        result = await db.execute(select(Client).where(Client.name == "Demo Farm"))
        existing_client = result.scalar_one_or_none()

        if existing_client:
            print(f"[OK] Demo client already exists (ID: {existing_client.id})")
            client = existing_client
        else:
            # Create demo client configuration
            client = Client(
                name="Demo Farm",
                dynamics_url="https://yourorg.crm3.dynamics.com",

                # IMPORTANT: These are Azure AD App Registration credentials for API access
                # NOT the user login credentials. These need to be replaced with real
                # Azure AD app credentials for production Dynamics 365 sync to work.
                # See .env.example for setup instructions.
                dynamics_client_id="YOUR_AZURE_AD_APP_CLIENT_ID",  # Replace with Azure AD App Client ID (GUID)
                dynamics_client_secret="YOUR_AZURE_AD_APP_SECRET",  # Replace with Azure AD App Secret
                dynamics_tenant_id="YOUR_AZURE_AD_TENANT_ID",  # Replace with Azure AD Tenant ID (GUID)

                is_active=True,

                # User login credentials (for dashboard login)
                # These are the credentials users use to log into the voice automation dashboard
                settings={
                    "username": "demo@example.com",
                    "password": "demo123",
                    "login_url": "https://yourorg.crm3.dynamics.com/",
                    "description": "Demo account for farm voice automation"
                }
            )
            db.add(client)
            await db.commit()
            await db.refresh(client)
            print(f"[OK] Created demo client: {client.name} (ID: {client.id})")

        # Check if schema mapping already exists
        result = await db.execute(
            select(SchemaMapping).where(
                SchemaMapping.client_id == client.id,
                SchemaMapping.entity_name == "animal"
            )
        )
        existing_mapping = result.scalar_one_or_none()

        if existing_mapping:
            print(f"[OK] Schema mapping already exists for {client.name}")
        else:
            # Create bioTrack animal schema mapping
            schema_mapping = SchemaMapping(
                client_id=client.id,
                entity_name="animal",
                dynamics_entity_name="biotrack_animals",
                field_mappings={
                    # Identification
                    "ear_tag": "bt_ear_tag",
                    "rfid": "bt_rfid",
                    "bio_id": "bt_bio_id",
                    "registration_name": "bt_registration_name",
                    "registration_id": "bt_registration_id",

                    # Basic Information
                    "category": "bt_category",
                    "species": "bt_species",
                    "sex": "bt_sex",
                    "birth_date": "bt_birth_date",
                    "location": "bt_location",

                    # Birth Information
                    "herd_letter": "bt_herd_letter",
                    "one_time_herd_letter": "bt_one_time_herd_letter",
                    "birth_season": "bt_birth_season",
                    "born_as": "bt_born_as",
                    "raised_as": "bt_raised_as",
                    "birthing_ease": "bt_birthing_ease",
                    "birth_weight": "bt_birth_weight",
                    "birth_weight_uom": "bt_birth_weight_uom",

                    # Parentage
                    "dam_id": "bt_dam_id",
                    "sire_id": "bt_sire_id",
                    "foster_id": "bt_foster_id",
                    "donor_id": "bt_donor_id",

                    # Physical Characteristics
                    "colour": "bt_colour",
                    "horn": "bt_horn",
                    "breed_composition": "bt_breed_composition",

                    # Comments
                    "animal_comments": "bt_comments"
                },
                validation_rules={
                    # Always required fields
                    "category": {"type": "string", "required": True},
                    "species": {"type": "string", "required": True},
                    "birth_date": {"type": "date", "required": True},
                    "sex": {"type": "string", "required": True},
                    "breed_composition": {"type": "object", "required": True},
                    "location": {"type": "string", "required": True},

                    # Conditionally required
                    "ear_tag": {"type": "string", "required": False, "unique": True},
                    "rfid": {"type": "string", "required": False, "pattern": r"^\d{15,20}$"},
                    "herd_letter": {"type": "string", "required": False},
                    "birth_season": {"type": "string", "required": False},
                    "birth_weight_uom": {"type": "string", "required": False},

                    # Optional fields
                    "registration_name": {"type": "string", "required": False},
                    "registration_id": {"type": "string", "required": False},
                    "born_as": {"type": "string", "required": False},
                    "raised_as": {"type": "string", "required": False},
                    "birthing_ease": {"type": "string", "required": False},
                    "birth_weight": {"type": "float", "required": False},
                    "dam_id": {"type": "string", "required": False},
                    "sire_id": {"type": "string", "required": False},
                    "colour": {"type": "string", "required": False},
                    "animal_comments": {"type": "string", "required": False}
                },
                detection_keywords=[
                    "animal", "cow", "cattle", "bull", "heifer", "steer",
                    "sheep", "lamb", "ewe", "ram",
                    "goat", "kid", "doe", "buck",
                    "bison", "buffalo",
                    "ear tag", "rfid", "tag number",
                    "birth", "born", "calving", "lambing",
                    "biotrack", "bio track"
                ],
                is_active=True
            )
            db.add(schema_mapping)
            await db.commit()
            print(f"[OK] Created bioTrack animal schema mapping for {client.name}")

        print("\n" + "="*70)
        print("✅ SUCCESS: Database seeded successfully!")
        print("="*70)
        print(f"\nDemo Client Configuration:")
        print(f"  Name: {client.name}")
        print(f"  ID: {client.id}")
        print(f"  Status: {'✅ Active' if client.is_active else '❌ Inactive'}")
        print(f"  Dynamics URL: {client.dynamics_url}")

        print(f"\n🔐 Dashboard Login Credentials (for farmers):")
        print(f"  Username: {client.settings.get('username')}")
        print(f"  Password: {client.settings.get('password')}")
        print(f"  Login URL: {client.settings.get('login_url')}")

        print(f"\n⚠️  Dynamics 365 API Credentials Status:")
        if client.dynamics_client_id.startswith("YOUR_"):
            print(f"  ❌ NOT CONFIGURED - Placeholder values detected")
            print(f"  📝 Action Required: Set up Azure AD App Registration")
            print(f"  📖 Instructions: See .env.example or CLIENT_HANDOVER.md")
            print(f"\n  ⚠️  Recordings will process but FAIL at Dynamics sync step")
            print(f"     until real Azure AD credentials are configured.")
        else:
            print(f"  ✅ CONFIGURED")
            print(f"  Client ID: {client.dynamics_client_id[:20]}...")

        print(f"\n🚀 Next Steps:")
        print(f"  1. Start server: python -m backend.main")
        print(f"  2. Visit: http://localhost:8000")
        print(f"  3. Login with: {client.settings.get('username')}")
        print(f"  4. Test voice recording → Dynamics sync flow")
        print(f"  5. View API docs: http://localhost:8000/docs")

        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(seed_demo_client())
