"""
OpenAI Whisper Speech-to-Text Service
Handles voice transcription using OpenAI Whisper API
"""
from openai import AsyncOpenAI
from backend.core.config import settings
import logging
import tempfile
import os

logger = logging.getLogger(__name__)


class WhisperService:
    """Service for OpenAI Whisper Speech-to-Text"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.WHISPER_API_KEY)
        self.model = settings.WHISPER_MODEL

    async def transcribe_audio(self, audio_content: bytes, filename: str = "audio.wav") -> dict:
        """
        Transcribe audio content to text using OpenAI Whisper API

        Args:
            audio_content: Audio file content as bytes
            filename: Original filename (used for file extension detection)

        Returns:
            Dictionary with transcription text and confidence level
        """
        try:
            # Whisper API requires a file object, so we use a temporary file
            # Determine file extension from filename
            file_extension = os.path.splitext(filename)[1] or '.wav'

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(audio_content)
                temp_file_path = temp_file.name

            try:
                # Open the temp file and send to Whisper API
                with open(temp_file_path, 'rb') as audio_file:
                    response = await self.client.audio.transcriptions.create(
                        model=self.model,
                        file=audio_file,
                        response_format="verbose_json"  # Get detailed response with confidence
                    )

                # Extract transcription text
                transcription_text = response.text

                # Whisper doesn't provide direct confidence scores in the simple response
                # In verbose_json mode, we can estimate based on response quality
                # For now, we'll use a simple heuristic
                if transcription_text and len(transcription_text.strip()) > 0:
                    confidence = "HIGH"
                else:
                    confidence = "LOW"

                logger.info(f"Transcription successful: {transcription_text[:100]}...")

                return {
                    "text": transcription_text,
                    "confidence": confidence,
                    "success": True
                }

            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"Error during Whisper transcription: {str(e)}")
            return {
                "text": "",
                "confidence": "LOW",
                "success": False,
                "error": str(e)
            }

    async def transcribe_audio_with_language(
        self,
        audio_content: bytes,
        language: str = "en",
        filename: str = "audio.wav"
    ) -> dict:
        """
        Transcribe audio content with specified language

        Args:
            audio_content: Audio file content as bytes
            language: ISO 639-1 language code (e.g., 'en', 'es', 'fr')
            filename: Original filename

        Returns:
            Dictionary with transcription text and confidence level
        """
        try:
            file_extension = os.path.splitext(filename)[1] or '.wav'

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(audio_content)
                temp_file_path = temp_file.name

            try:
                with open(temp_file_path, 'rb') as audio_file:
                    response = await self.client.audio.transcriptions.create(
                        model=self.model,
                        file=audio_file,
                        language=language,
                        response_format="verbose_json"
                    )

                transcription_text = response.text
                confidence = "HIGH" if transcription_text and len(transcription_text.strip()) > 0 else "LOW"

                logger.info(f"Transcription successful (language: {language}): {transcription_text[:100]}...")

                return {
                    "text": transcription_text,
                    "confidence": confidence,
                    "success": True,
                    "language": language
                }

            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"Error during Whisper transcription with language: {str(e)}")
            return {
                "text": "",
                "confidence": "LOW",
                "success": False,
                "error": str(e)
            }
