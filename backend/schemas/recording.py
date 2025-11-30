"""
Recording schemas for API validation and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime
from uuid import UUID
from backend.models.recording import RecordingStatus


class RecordingBase(BaseModel):
    """Base recording schema"""
    filename: str


class RecordingCreate(RecordingBase):
    """Schema for creating a recording"""
    client_id: UUID


class RecordingResponse(BaseModel):
    """Schema for recording response"""
    id: UUID
    client_id: UUID
    filename: str
    blob_url: str
    file_size: Optional[int]
    content_type: Optional[str]
    status: RecordingStatus
    transcription_text: Optional[str]
    transcription_confidence: Optional[str]
    extracted_data: Optional[Dict]
    entity_type: Optional[str]
    confidence_score: Optional[str]
    dynamics_record_id: Optional[str]
    sync_error: Optional[str]
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class RecordingUploadResponse(BaseModel):
    """Schema for upload response"""
    recording_id: UUID
    message: str
    status: str
