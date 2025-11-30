"""
Azure Speech-to-Text Service
Handles voice transcription using Azure Cognitive Services
"""
import azure.cognitiveservices.speech as speechsdk
from backend.core.config import settings
import logging
import tempfile
import os

logger = logging.getLogger(__name__)


class AzureSpeechService:
    """Service for Azure Speech-to-Text"""

    def __init__(self):
        self.speech_key = settings.AZURE_SPEECH_KEY
        self.speech_region = settings.AZURE_SPEECH_REGION

    async def transcribe_audio(self, audio_content: bytes) -> dict:
        """
        Transcribe audio content to text

        Args:
            audio_content: Audio file content as bytes

        Returns:
            Dictionary with transcription text and confidence level
        """
        try:
            # Create speech config
            speech_config = speechsdk.SpeechConfig(
                subscription=self.speech_key,
                region=self.speech_region
            )

            # Set recognition language (can be made configurable)
            speech_config.speech_recognition_language = "en-US"

            # Save audio to temporary file (Azure SDK requires file path)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_content)
                temp_file_path = temp_file.name

            try:
                # Create audio config from file
                audio_config = speechsdk.AudioConfig(filename=temp_file_path)

                # Create speech recognizer
                speech_recognizer = speechsdk.SpeechRecognizer(
                    speech_config=speech_config,
                    audio_config=audio_config
                )

                # Perform recognition
                result = speech_recognizer.recognize_once()

                # Process result
                if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    logger.info(f"Transcription successful: {result.text[:100]}...")

                    # Determine confidence level based on Azure's internal scoring
                    # Note: Azure doesn't always provide confidence, so we estimate
                    confidence = "HIGH"  # Default for successful recognition

                    return {
                        "text": result.text,
                        "confidence": confidence,
                        "success": True
                    }

                elif result.reason == speechsdk.ResultReason.NoMatch:
                    logger.warning("No speech could be recognized")
                    return {
                        "text": "",
                        "confidence": "LOW",
                        "success": False,
                        "error": "No speech recognized"
                    }

                elif result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = result.cancellation_details
                    logger.error(f"Speech recognition canceled: {cancellation.reason}")

                    if cancellation.reason == speechsdk.CancellationReason.Error:
                        logger.error(f"Error details: {cancellation.error_details}")

                    return {
                        "text": "",
                        "confidence": "LOW",
                        "success": False,
                        "error": str(cancellation.reason)
                    }

            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            return {
                "text": "",
                "confidence": "LOW",
                "success": False,
                "error": str(e)
            }
