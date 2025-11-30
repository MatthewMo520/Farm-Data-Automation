"""
Client model for multi-tenant support
"""
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from backend.core.database import Base


class Client(Base):
    """Client/Tenant model"""
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)

    # Dynamics 365 credentials (encrypted in production)
    dynamics_url = Column(String(500), nullable=False)
    dynamics_client_id = Column(String(255), nullable=False)
    dynamics_client_secret = Column(Text, nullable=False)  # Should be encrypted
    dynamics_tenant_id = Column(String(255), nullable=False)

    # Client status
    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Additional settings (JSON)
    settings = Column(JSON, default={})

    # Relationships
    recordings = relationship("Recording", back_populates="client", cascade="all, delete-orphan")
    schema_mappings = relationship("SchemaMapping", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(id={self.id}, name={self.name})>"
