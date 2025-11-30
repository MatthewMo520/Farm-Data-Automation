"""
Schema mapping schemas for API validation and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
from uuid import UUID


class SchemaMappingBase(BaseModel):
    """Base schema mapping"""
    entity_name: str = Field(..., min_length=1, max_length=255)
    dynamics_entity_name: str = Field(..., min_length=1, max_length=255)
    field_mappings: Dict = Field(default_factory=dict)
    validation_rules: Dict = Field(default_factory=dict)
    detection_keywords: List[str] = Field(default_factory=list)


class SchemaMappingCreate(SchemaMappingBase):
    """Schema for creating a schema mapping"""
    client_id: UUID
    description: Optional[str] = None


class SchemaMappingUpdate(BaseModel):
    """Schema for updating a schema mapping"""
    entity_name: Optional[str] = None
    dynamics_entity_name: Optional[str] = None
    field_mappings: Optional[Dict] = None
    validation_rules: Optional[Dict] = None
    detection_keywords: Optional[List[str]] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class SchemaMappingResponse(SchemaMappingBase):
    """Schema for schema mapping response"""
    id: UUID
    client_id: UUID
    is_active: bool
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
