"""
Recording Processor Worker
Orchestrates the entire pipeline: Upload -> Transcription -> AI Extraction -> Dynamics Sync
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from datetime import datetime
import logging
from uuid import UUID

from backend.core.config import settings
from backend.models.recording import Recording, RecordingStatus
from backend.models.client import Client
from backend.models.schema_mapping import SchemaMapping
from backend.services.azure_storage import AzureStorageService
from backend.services.azure_speech import AzureSpeechService
from backend.services.azure_openai import AzureOpenAIService
from backend.services.dynamics_client import DynamicsClient

logger = logging.getLogger(__name__)

# Create async engine for background workers
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def process_recording_async(recording_id: UUID):
    """
    Queue a recording for async processing
    In production, this would push to a message queue (Azure Service Bus, Redis, etc.)
    For MVP, we'll process directly
    """
    # Start processing in background
    asyncio.create_task(process_recording(recording_id))


async def process_recording(recording_id: UUID):
    """
    Main processing pipeline for a recording

    Steps:
    1. Download audio file from Azure Storage
    2. Transcribe audio using Azure Speech-to-Text
    3. Extract structured data using Azure OpenAI
    4. Map data to Dynamics 365 fields
    5. Create record in Dynamics 365
    """
    logger.info(f"Starting processing for recording {recording_id}")

    async with AsyncSessionLocal() as db:
        try:
            # Get recording
            result = await db.execute(select(Recording).where(Recording.id == recording_id))
            recording = result.scalar_one_or_none()

            if not recording:
                logger.error(f"Recording {recording_id} not found")
                return

            # Get client
            result = await db.execute(select(Client).where(Client.id == recording.client_id))
            client = result.scalar_one_or_none()

            if not client:
                logger.error(f"Client {recording.client_id} not found")
                return

            # Step 1: Download audio file
            logger.info(f"[{recording_id}] Step 1: Downloading audio file")
            storage_service = AzureStorageService()
            audio_content = await storage_service.download_file(recording.blob_url)

            # Step 2: Transcribe audio
            logger.info(f"[{recording_id}] Step 2: Transcribing audio")
            recording.status = RecordingStatus.TRANSCRIBING
            await db.commit()

            speech_service = AzureSpeechService()
            transcription_result = await speech_service.transcribe_audio(audio_content)

            if not transcription_result.get("success"):
                recording.status = RecordingStatus.FAILED
                recording.sync_error = f"Transcription failed: {transcription_result.get('error')}"
                await db.commit()
                logger.error(f"[{recording_id}] Transcription failed")
                return

            recording.transcription_text = transcription_result["text"]
            recording.transcription_confidence = transcription_result["confidence"]
            recording.status = RecordingStatus.TRANSCRIBED
            await db.commit()

            logger.info(f"[{recording_id}] Transcription successful")

            # Step 3: Extract data using AI
            logger.info(f"[{recording_id}] Step 3: Extracting data with AI")
            recording.status = RecordingStatus.PROCESSING
            await db.commit()

            # Get schema mappings for client
            result = await db.execute(
                select(SchemaMapping).where(
                    SchemaMapping.client_id == client.id,
                    SchemaMapping.is_active == True
                )
            )
            schema_mappings = result.scalars().all()

            if not schema_mappings:
                logger.warning(f"[{recording_id}] No schema mappings found for client {client.name}")
                recording.status = RecordingStatus.FAILED
                recording.sync_error = "No schema mappings configured for this client"
                await db.commit()
                return

            # Convert schema mappings to dict format for AI
            schema_dicts = [
                {
                    "entity_name": sm.entity_name,
                    "field_mappings": sm.field_mappings,
                    "validation_rules": sm.validation_rules,
                    "detection_keywords": sm.detection_keywords
                }
                for sm in schema_mappings
            ]

            openai_service = AzureOpenAIService()
            extraction_result = await openai_service.extract_data_from_transcription(
                recording.transcription_text,
                schema_dicts
            )

            entity_type = extraction_result.get("entity_type")
            extracted_data = extraction_result.get("extracted_data", {})
            confidence = extraction_result.get("confidence", "LOW")

            if entity_type == "unknown":
                recording.status = RecordingStatus.FAILED
                recording.sync_error = "Could not determine entity type from transcription"
                recording.extracted_data = extraction_result
                await db.commit()
                logger.error(f"[{recording_id}] Unknown entity type")
                return

            recording.entity_type = entity_type
            recording.extracted_data = extraction_result
            recording.confidence_score = confidence
            await db.commit()

            logger.info(f"[{recording_id}] Data extraction successful. Entity: {entity_type}")

            # Step 4: Map to Dynamics 365 fields
            logger.info(f"[{recording_id}] Step 4: Mapping to Dynamics 365 fields")

            # Find matching schema mapping
            matching_schema = next(
                (sm for sm in schema_mappings if sm.entity_name == entity_type),
                None
            )

            if not matching_schema:
                recording.status = RecordingStatus.FAILED
                recording.sync_error = f"No schema mapping found for entity type: {entity_type}"
                await db.commit()
                return

            # Validate extracted data
            validation_result = await openai_service.validate_extracted_data(
                extracted_data,
                matching_schema.validation_rules
            )

            if not validation_result["is_valid"]:
                recording.status = RecordingStatus.FAILED
                recording.sync_error = f"Validation errors: {', '.join(validation_result['errors'])}"
                await db.commit()
                logger.error(f"[{recording_id}] Validation failed")
                return

            # Map fields to Dynamics format
            dynamics_data = {}
            for ai_field, dynamics_field in matching_schema.field_mappings.items():
                if ai_field in extracted_data:
                    dynamics_data[dynamics_field] = extracted_data[ai_field]

            logger.info(f"[{recording_id}] Mapped data to Dynamics fields")

            # Step 5: Create record in Dynamics 365
            logger.info(f"[{recording_id}] Step 5: Creating record in Dynamics 365")

            dynamics_client = DynamicsClient(
                base_url=client.dynamics_url,
                client_id=client.dynamics_client_id,
                client_secret=client.dynamics_client_secret,
                tenant_id=client.dynamics_tenant_id
            )

            dynamics_result = await dynamics_client.create_record(
                entity_name=matching_schema.dynamics_entity_name,
                data=dynamics_data
            )

            recording.dynamics_record_id = dynamics_result["id"]
            recording.status = RecordingStatus.SYNCED
            recording.processed_at = datetime.utcnow()
            await db.commit()

            logger.info(f"[{recording_id}] Successfully synced to Dynamics 365. Record ID: {dynamics_result['id']}")

        except Exception as e:
            logger.error(f"[{recording_id}] Error processing recording: {str(e)}")
            recording.status = RecordingStatus.FAILED
            recording.sync_error = str(e)
            await db.commit()
