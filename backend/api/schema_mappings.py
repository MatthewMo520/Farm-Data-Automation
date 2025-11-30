"""
Schema Mapping management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from backend.core.database import get_db
from backend.models.schema_mapping import SchemaMapping
from backend.models.client import Client
from backend.schemas.schema_mapping import (
    SchemaMappingCreate,
    SchemaMappingResponse,
    SchemaMappingUpdate
)

router = APIRouter()


@router.post("/schema-mappings", response_model=SchemaMappingResponse, status_code=status.HTTP_201_CREATED)
async def create_schema_mapping(
    mapping_data: SchemaMappingCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new schema mapping for a client"""
    # Verify client exists
    result = await db.execute(select(Client).where(Client.id == mapping_data.client_id))
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id '{mapping_data.client_id}' not found"
        )

    # Create mapping
    new_mapping = SchemaMapping(**mapping_data.model_dump())
    db.add(new_mapping)
    await db.commit()
    await db.refresh(new_mapping)

    return new_mapping


@router.get("/schema-mappings", response_model=List[SchemaMappingResponse])
async def list_schema_mappings(
    client_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List schema mappings, optionally filtered by client"""
    query = select(SchemaMapping)

    if client_id:
        query = query.where(SchemaMapping.client_id == client_id)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    mappings = result.scalars().all()

    return mappings


@router.get("/schema-mappings/{mapping_id}", response_model=SchemaMappingResponse)
async def get_schema_mapping(
    mapping_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific schema mapping"""
    result = await db.execute(select(SchemaMapping).where(SchemaMapping.id == mapping_id))
    mapping = result.scalar_one_or_none()

    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema mapping with id '{mapping_id}' not found"
        )

    return mapping


@router.patch("/schema-mappings/{mapping_id}", response_model=SchemaMappingResponse)
async def update_schema_mapping(
    mapping_id: UUID,
    mapping_data: SchemaMappingUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a schema mapping"""
    result = await db.execute(select(SchemaMapping).where(SchemaMapping.id == mapping_id))
    mapping = result.scalar_one_or_none()

    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema mapping with id '{mapping_id}' not found"
        )

    # Update fields
    update_data = mapping_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mapping, field, value)

    await db.commit()
    await db.refresh(mapping)

    return mapping


@router.delete("/schema-mappings/{mapping_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schema_mapping(
    mapping_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a schema mapping"""
    result = await db.execute(select(SchemaMapping).where(SchemaMapping.id == mapping_id))
    mapping = result.scalar_one_or_none()

    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema mapping with id '{mapping_id}' not found"
        )

    await db.delete(mapping)
    await db.commit()

    return None
