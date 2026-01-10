"""
Recording Processor Worker

This is the MAIN PROCESSING PIPELINE that orchestrates the entire voice-to-database workflow.

Pipeline Flow:
    1. Upload → File saved to local storage (./storage/recordings/)
    2. Transcription → Audio converted to text using OpenAI Whisper API (~$0.006/min)
    3. AI Extraction → Structured data extracted using Groq AI (FREE)
    4. Validation → Check against bioTrack+ required fields
    5. Dynamics Sync → Create animal record in Microsoft Dynamics 365

Status Progression:
    UPLOADED → TRANSCRIBING → TRANSCRIBED → PROCESSING → SYNCED/FAILED

Error Handling:
    - Each step can fail independently
    - Errors are captured in recording.sync_error for user display
    - Failed recordings can be reprocessed via POST /api/v1/recordings/{id}/reprocess

Key Features:
    - Async processing using SQLAlchemy async sessions
    - Detailed logging for each processing step
    - Missing field detection with helpful error messages
    - Automatic field mapping from AI output to Dynamics schema
    - Support for multi-tenant (per-client schema mappings)

Cost Breakdown (per recording):
    - Storage: FREE (local filesystem)
    - Transcription: ~$0.006 per minute of audio
    - AI Extraction: FREE (Groq free tier: 14,400 requests/day)
    - Database: FREE (SQLite) or cloud PostgreSQL (~$5-10/month)
    Total: ~$0.006 per minute of audio

Usage:
    # Trigger processing for a new recording
    await process_recording_async(recording_id)

    # Or process synchronously (for testing)
    await process_recording(recording_id)

Author: Farm Data Automation Team
Version: 2.0 (Post-Azure migration)
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
from backend.services.local_storage import LocalStorageService
from backend.services.whisper_service import WhisperService
from backend.services.whisper_local import LocalWhisperService
from backend.services.groq_service import GroqService
from backend.services.dynamics_client import DynamicsClient

# bioTrack animal validation
from backend.schemas.biotrack_animal import get_missing_required_fields, format_missing_fields_prompt

logger = logging.getLogger(__name__)

# Create async engine for background workers
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def process_recording_async(recording_id: UUID):
    """
    Queue a recording for asynchronous background processing

    This function triggers the processing pipeline without blocking the API response.
    The client can poll the recording status to track progress.

    Implementation Note:
        Currently uses asyncio.create_task() for in-process background execution.
        In production, this should be replaced with a proper message queue system:
        - Azure Service Bus
        - Redis Queue (RQ)
        - Celery with Redis/RabbitMQ
        - AWS SQS

    Args:
        recording_id (UUID): Unique identifier of the recording to process

    Returns:
        None (processing happens in background)

    Status Updates:
        The recording status is updated in the database as processing progresses:
        - UPLOADED: Initial state after file upload
        - TRANSCRIBING: Whisper API is converting audio to text
        - TRANSCRIBED: Audio successfully converted to text
        - PROCESSING: AI is extracting structured data
        - SYNCED: Successfully synced to Dynamics 365
        - FAILED: An error occurred (check recording.sync_error for details)
    """
    # Start processing in background (non-blocking)
    asyncio.create_task(process_recording(recording_id))


async def process_recording(recording_id: UUID):
    """
    Main processing pipeline for a voice recording

    This function orchestrates the complete end-to-end workflow from audio file
    to Dynamics 365 database record. It handles all processing steps, error handling,
    status updates, and validation.

    Processing Steps:
        1. Download Audio File
           - Retrieves audio file from local storage (./storage/recordings/)
           - Validates file exists and is accessible

        2. Transcribe Audio (OpenAI Whisper)
           - Converts speech to text using Whisper API
           - Cost: ~$0.006 per minute of audio
           - Updates status: UPLOADED → TRANSCRIBING → TRANSCRIBED
           - Stores transcription_text and confidence score

        3. Extract Structured Data (Groq AI)
           - Uses Groq AI (Llama 3.1 70B) to extract fields from text
           - FREE tier: 14,400 requests/day
           - Detects entity type (animal, farm, treatment, etc.)
           - Extracts relevant fields based on schema mappings
           - Updates status: TRANSCRIBED → PROCESSING

        4. Validate Required Fields
           - Checks against bioTrack+ field requirements
           - Identifies missing required fields
           - Fails with helpful error message if incomplete
           - See backend/schemas/biotrack_animal.py for validation logic

        5. Map to Dynamics Schema
           - Converts AI field names to Dynamics 365 field names
           - Uses client-specific schema mappings from database
           - Applies validation rules (type checking, patterns, etc.)

        6. Sync to Dynamics 365
           - Authenticates with Azure AD OAuth2
           - Creates record via Dynamics Web API (OData v4.0)
           - Stores returned dynamics_record_id
           - Updates status: PROCESSING → SYNCED
           - Records processed_at timestamp

    Args:
        recording_id (UUID): Unique identifier of the recording to process

    Returns:
        None (results are stored in database)

    Side Effects:
        - Updates recording status in database after each step
        - Stores transcription, extracted_data, and sync results
        - Sets recording.sync_error if any step fails
        - Logs detailed progress to application logs

    Error Handling:
        - Each step validates before proceeding
        - Failures set status to FAILED with descriptive error message
        - Missing fields prompt user with specific list of needed info
        - All exceptions are caught, logged, and stored in sync_error

    Example Error Messages:
        - "Transcription failed: Invalid audio format"
        - "Missing required fields: ear_tag, birth_date, sex"
        - "No schema mapping found for entity type: treatment"
        - "Validation errors: birth_date must be in YYYY-MM-DD format"
        - "Dynamics sync failed: Unauthorized - check client credentials"

    Database Changes:
        - Updates recording.status multiple times during processing
        - Sets recording.transcription_text after step 2
        - Sets recording.extracted_data after step 3
        - Sets recording.dynamics_record_id after step 6
        - Sets recording.processed_at timestamp when complete
        - Sets recording.sync_error if failed at any step
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

            # Download from local storage
            if not recording.file_path:
                raise ValueError("No file path found for recording")

            storage_service = LocalStorageService()
            audio_content = await storage_service.download_file(recording.file_path)

            # Step 2: Transcribe audio
            logger.info(f"[{recording_id}] Step 2: Transcribing audio")
            recording.status = RecordingStatus.TRANSCRIBING
            await db.commit()

            # Choose transcription service based on config
            if settings.WHISPER_MODE == "local":
                logger.info(f"[{recording_id}] Using FREE local Whisper (model: {settings.WHISPER_LOCAL_MODEL})")
                speech_service = LocalWhisperService(model_name=settings.WHISPER_LOCAL_MODEL)
            else:
                logger.info(f"[{recording_id}] Using OpenAI Whisper API (cost: ~$0.006/min)")
                speech_service = WhisperService()

            transcription_result = await speech_service.transcribe_audio(audio_content, recording.filename)

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

            ai_service = GroqService()
            extraction_result = await ai_service.extract_with_retry(
                recording.transcription_text,
                schema_dicts,
                max_retries=3
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

            # Check for missing required fields
            missing_fields = get_missing_required_fields(
                extracted_data,
                extracted_data.get("category")
            )

            if missing_fields:
                # Store missing fields information
                recording.sync_error = format_missing_fields_prompt(missing_fields)
                recording.status = RecordingStatus.FAILED
                await db.commit()
                logger.warning(f"[{recording_id}] Missing required fields: {missing_fields}")
                return

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
            validation_result = await ai_service.validate_extracted_data(
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
