"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.client import Client

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model"""
    message: str
    client: dict


@router.post("/auth/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user with bioTrack+ credentials

    This endpoint validates user login credentials against stored client information.
    For demo/testing, credentials are stored in the client.settings JSON field.

    Demo Credentials:
        Username: demo@biotrack.ca
        Password: bioTrack+test
        URL: https://agsights.crm3.dynamics.com

    Request Body:
        {
            "username": "demo@biotrack.ca",
            "password": "bioTrack+test"
        }

    Response:
        {
            "message": "Login successful",
            "client": {
                "id": "uuid",
                "name": "bioTrack+ Demo",
                "dynamics_url": "https://agsights.crm3.dynamics.com",
                "is_active": true
            }
        }

    Note:
        In production, this should integrate with Microsoft Dynamics 365 OAuth 2.0
        for proper single sign-on authentication. Current implementation is for
        demo/testing purposes only.
    """
    # Find all active clients
    result = await db.execute(
        select(Client).where(Client.is_active == True)
    )
    clients = result.scalars().all()

    # Check each client's settings for matching username
    for client in clients:
        # Check if username matches in settings
        client_username = client.settings.get("username") if client.settings else None

        if client_username == credentials.username:
            # Validate password
            client_password = client.settings.get("password") if client.settings else None

            if client_password == credentials.password:
                # Login successful!
                return LoginResponse(
                    message="Login successful",
                    client={
                        "id": str(client.id),
                        "name": client.name,
                        "dynamics_url": client.dynamics_url,
                        "is_active": client.is_active
                    }
                )

    # No matching credentials found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password. Please check your bioTrack+ credentials and try again."
    )


@router.post("/auth/logout")
async def logout():
    """Logout endpoint (for future session management)"""
    return {"message": "Logged out successfully"}
