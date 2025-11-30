"""
Recording management and upload endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
import logging

from backend.core.database import get_db
from backend.models.recording import Recording
from backend.schemas.recording import RecordingResponse, RecordingUploadResponse
from backend.services.azure_storage import AzureStorageService
from backend.workers.recording_processor import process_recording_async

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/recordings/upload", response_model=RecordingUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_recording(
    client_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a voice recording for processing

    This endpoint:
    1. Validates the client exists
    2. Uploads the file to Azure Blob Storage
    3. Creates a recording record in the database
    4. Triggers async processing (transcription -> AI extraction -> Dynamics sync)
    """
    # Validate client exists
    from backend.models.client import Client
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client with id '{client_id}' not found"
        )

    if not client.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Client '{client.name}' is not active"
        )

    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)

        # Upload to Azure Blob Storage
        storage_service = AzureStorageService()
        blob_url = await storage_service.upload_file(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )

        # Create recording record
        recording = Recording(
            client_id=client_id,
            filename=file.filename,
            blob_url=blob_url,
            file_size=file_size,
            content_type=file.content_type
        )

        db.add(recording)
        await db.commit()
        await db.refresh(recording)

        # Trigger async processing
        await process_recording_async(recording.id)

        logger.info(f"Recording {recording.id} uploaded successfully for client {client.name}")

        return RecordingUploadResponse(
            recording_id=recording.id,
            message="Recording uploaded successfully and queued for processing",
            status="uploaded"
        )

    except Exception as e:
        logger.error(f"Error uploading recording: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading recording: {str(e)}"
        )


@router.get("/recordings", response_model=List[RecordingResponse])
async def list_recordings(
    client_id: UUID = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List recordings, optionally filtered by client"""
    query = select(Recording)

    if client_id:
        query = query.where(Recording.client_id == client_id)

    query = query.offset(skip).limit(limit).order_by(Recording.created_at.desc())

    result = await db.execute(query)
    recordings = result.scalars().all()

    return recordings


@router.get("/recordings/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific recording"""
    result = await db.execute(select(Recording).where(Recording.id == recording_id))
    recording = result.scalar_one_or_none()

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording with id '{recording_id}' not found"
        )

    return recording


@router.post("/recordings/{recording_id}/reprocess", response_model=RecordingResponse)
async def reprocess_recording(
    recording_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Reprocess a failed or completed recording"""
    result = await db.execute(select(Recording).where(Recording.id == recording_id))
    recording = result.scalar_one_or_none()

    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recording with id '{recording_id}' not found"
        )

    # Reset status
    from backend.models.recording import RecordingStatus
    recording.status = RecordingStatus.UPLOADED
    recording.sync_error = None

    await db.commit()
    await db.refresh(recording)

    # Trigger async processing
    await process_recording_async(recording.id)

    return recording
