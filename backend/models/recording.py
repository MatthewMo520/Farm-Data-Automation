"""
Recording model for voice recordings and processing
"""
from sqlalchemy import Column, String, DateTime, Text, Enum, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from backend.core.database import Base


class RecordingStatus(str, enum.Enum):
    """Recording processing status"""
    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    TRANSCRIBED = "transcribed"
    PROCESSING = "processing"
    PROCESSED = "processed"
    SYNCED = "synced"
    FAILED = "failed"


class Recording(Base):
    """Voice recording model"""
    __tablename__ = "recordings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)

    # File information
    filename = Column(String(500), nullable=False)
    blob_url = Column(Text, nullable=True)  # Legacy Azure storage (nullable for migration)
    file_path = Column(Text, nullable=True)  # New local storage path
    file_size = Column(Integer)
    content_type = Column(String(100))

    # Processing status
    status = Column(Enum(RecordingStatus), default=RecordingStatus.UPLOADED, nullable=False)

    # Transcription
    transcription_text = Column(Text)
    transcription_confidence = Column(String(10))  # LOW, MEDIUM, HIGH

    # AI Processing
    extracted_data = Column(JSON)  # Extracted fields from AI
    entity_type = Column(String(100))  # Dynamics entity type (e.g., "animal", "farm")
    confidence_score = Column(String(10))

    # Dynamics 365 sync
    dynamics_record_id = Column(String(255))  # ID in Dynamics 365
    sync_error = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime)

    # Relationships
    client = relationship("Client", back_populates="recordings")

    def __repr__(self):
        return f"<Recording(id={self.id}, filename={self.filename}, status={self.status})>"
