"""
Schema mapping model for client-specific Dynamics 365 field mappings
"""
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.core.database import Base


class SchemaMapping(Base):
    """Schema mapping for client-specific Dynamics 365 entities"""
    __tablename__ = "schema_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)

    # Entity information
    entity_name = Column(String(255), nullable=False)  # e.g., "animal", "farm", "treatment"
    dynamics_entity_name = Column(String(255), nullable=False)  # Actual Dynamics entity name

    # Field mappings (JSON structure)
    # Format: {"ai_field": "dynamics_field", "animal_id": "msdyn_animalid", ...}
    field_mappings = Column(JSON, nullable=False, default={})

    # Validation rules (JSON structure)
    # Format: {"field_name": {"type": "string", "required": true, "pattern": "..."}}
    validation_rules = Column(JSON, default={})

    # Keywords/triggers for entity detection
    # List of keywords that indicate this entity type
    detection_keywords = Column(JSON, default=[])

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Description/notes
    description = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    client = relationship("Client", back_populates="schema_mappings")

    def __repr__(self):
        return f"<SchemaMapping(id={self.id}, entity={self.entity_name})>"
