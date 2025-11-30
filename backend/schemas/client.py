"""
Client schemas for API validation and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID


class ClientBase(BaseModel):
    """Base client schema"""
    name: str = Field(..., min_length=1, max_length=255)
    dynamics_url: str
    dynamics_client_id: str
    dynamics_tenant_id: str


class ClientCreate(ClientBase):
    """Schema for creating a client"""
    dynamics_client_secret: str
    settings: Optional[Dict] = {}


class ClientUpdate(BaseModel):
    """Schema for updating a client"""
    name: Optional[str] = None
    dynamics_url: Optional[str] = None
    dynamics_client_id: Optional[str] = None
    dynamics_client_secret: Optional[str] = None
    dynamics_tenant_id: Optional[str] = None
    is_active: Optional[bool] = None
    settings: Optional[Dict] = None


class ClientResponse(ClientBase):
    """Schema for client response"""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    settings: Dict

    class Config:
        from_attributes = True
