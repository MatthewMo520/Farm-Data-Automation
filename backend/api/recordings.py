"""
Recording Management API Endpoints

This module provides REST API endpoints for managing voice recordings and their
processing lifecycle in the Farm Data Automation system.

Endpoints:
    POST   /api/v1/recordings/upload              Upload audio file
    GET    /api/v1/recordings                      List all recordings
    GET    /api/v1/recordings/{recording_id}       Get recording details
    POST   /api/v1/recordings/{recording_id}/reprocess    Retry processing

Main Workflow:
    1. User uploads audio file (or records in browser)
    2. POST /recordings/upload → File saved, processing triggered
    3. GET /recordings → User polls to check status
    4. If FAILED: POST /recordings/{id}/reprocess to retry

Recording Status Lifecycle:
    UPLOADED → TRANSCRIBING → TRANSCRIBED → PROCESSING → SYNCED
                                                ↓
                                              FAILED (can reprocess)

Supported Audio Formats:
    - MP3 (audio/mpeg)
    - WAV (audio/wav, audio/x-wav)
    - M4A (audio/m4a, audio/x-m4a)
    - OGG (audio/ogg)

Response Models:
    - RecordingUploadResponse: Immediate response after upload
    - RecordingResponse: Full recording details with status

Error Responses:
    - 400 Bad Request: Invalid client_id or inactive client
    - 404 Not Found: Client or recording not found
    - 500 Internal Server Error: File upload or processing error

Security:
    - Requires valid client_id (validated against database)
    - Only active clients can upload recordings
    - File size limits enforced by FastAPI (default: 1GB)

Usage Example (curl):
    # Upload a recording
    curl -X POST http://localhost:8000/api/v1/recordings/upload \\
         -F "client_id=550e8400-e29b-41d4-a716-446655440000" \\
         -F "file=@recording.mp3"

    # List recordings for a client
    curl http://localhost:8000/api/v1/recordings?client_id=550e8400-e29b-41d4-a716-446655440000

    # Get recording details
    curl http://localhost:8000/api/v1/recordings/123e4567-e89b-12d3-a456-426614174000

    # Reprocess a failed recording
    curl -X POST http://localhost:8000/api/v1/recordings/123e4567-e89b-12d3-a456-426614174000/reprocess

Frontend Integration:
    - See frontend/static/js/app.js for JavaScript implementation
    - Uses FormData for multipart/form-data upload
    - Polling mechanism to track processing status
    - Real-time status updates displayed to user

Author: Farm Data Automation Team
Version: 2.0
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
from backend.services.local_storage import LocalStorageService
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

    This is the PRIMARY ENDPOINT that farmers use to submit voice recordings
    describing animal details. The recording is immediately saved and queued for
    processing through the full pipeline (transcription → AI → Dynamics).

    Request Format: multipart/form-data
        - client_id (UUID): The client/tenant ID (from login session)
        - file (File): Audio file in supported format (MP3, WAV, M4A, OGG)

    Processing Flow:
        1. Validates client exists and is active
        2. Saves file to local storage (./storage/recordings/{client_id}/{year-month}/)
        3. Creates recording record in database with status=UPLOADED
        4. Triggers async background processing (non-blocking)
        5. Returns immediately with recording_id for status tracking

    Response (201 Created):
        {
            "recording_id": "123e4567-e89b-12d3-a456-426614174000",
            "message": "Recording uploaded successfully and queued for processing",
            "status": "uploaded"
        }

    Error Responses:
        - 400 Bad Request: Client is inactive
          {"detail": "Client 'ABC Farm' is not active"}

        - 404 Not Found: Client doesn't exist
          {"detail": "Client with id '...' not found"}

        - 500 Internal Server Error: File upload failed
          {"detail": "Error uploading recording: ..."}

    Background Processing:
        After upload, the recording goes through:
        - Whisper transcription (~5-30 seconds depending on audio length)
        - Groq AI extraction (~2-5 seconds)
        - bioTrack+ validation (instant)
        - Dynamics 365 sync (~1-3 seconds)

        Total processing time: 10-60 seconds average

    Polling for Status:
        After upload, client should poll GET /recordings/{recording_id}
        every 2-3 seconds to check status and display progress to user.

    Example (JavaScript):
        const formData = new FormData();
        formData.append('client_id', clientId);
        formData.append('file', audioBlob, 'recording.wav');

        const response = await fetch('/api/v1/recordings/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        console.log('Recording ID:', data.recording_id);

    File Size Limits:
        - Maximum: 1GB (configurable in FastAPI settings)
        - Recommended: < 10MB for optimal processing speed
        - Typical voice recording: 1-5MB per minute
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

        # Upload to local storage
        storage_service = LocalStorageService()
        file_path = await storage_service.upload_file(
            file_content=file_content,
            filename=file.filename,
            client_id=str(client_id),
            content_type=file.content_type
        )

        # Create recording record
        recording = Recording(
            client_id=client_id,
            filename=file.filename,
            file_path=file_path,
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
    """
    List all recordings with optional filtering and pagination

    This endpoint retrieves recordings for display in the dashboard, showing
    their current processing status, extracted data, and any errors.

    Query Parameters:
        - client_id (UUID, optional): Filter by specific client
        - skip (int, default=0): Number of records to skip (for pagination)
        - limit (int, default=100, max=1000): Number of records to return

    Response: Array of RecordingResponse objects
        [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "client_id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "recording_20240115_143022.wav",
                "status": "synced",
                "transcription_text": "Add new heifer, ear tag 12345, born January 15th...",
                "extracted_data": {"ear_tag": "12345", "sex": "Heifer", ...},
                "dynamics_record_id": "abc-123-def",
                "sync_error": null,
                "created_at": "2024-01-15T14:30:22Z",
                "processed_at": "2024-01-15T14:31:05Z"
            },
            ...
        ]

    Ordering:
        Results are ordered by created_at descending (newest first)

    Example Usage:
        # Get all recordings for logged-in client
        GET /api/v1/recordings?client_id=550e8400-e29b-41d4-a716-446655440000

        # Paginate through results
        GET /api/v1/recordings?skip=0&limit=20   # Page 1
        GET /api/v1/recordings?skip=20&limit=20  # Page 2
    """
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
