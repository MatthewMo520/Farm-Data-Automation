"""
Local Whisper Speech-to-Text Service (100% FREE)

This module provides FREE audio transcription using OpenAI's Whisper model
running locally on your server. No API keys or costs required!

Cost: $0 (completely free)
Speed: 10-30 seconds per recording (depending on hardware and model size)
Privacy: Audio never leaves your server
Requirements: ~1-3GB disk space for model, works on CPU (GPU faster)

Installation:
    pip install openai-whisper

Models Available:
    - tiny: Fastest, lowest quality (~75MB)
    - base: Good balance (~142MB) - RECOMMENDED
    - small: Better quality (~466MB)
    - medium: High quality (~1.5GB)
    - large: Best quality (~2.9GB)

Usage:
    service = LocalWhisperService(model_name="base")
    result = await service.transcribe_audio(audio_bytes, "recording.mp3")

Author: Farm Data Automation Team
Version: 2.0
"""
import whisper
import tempfile
import os
import asyncio
import logging
from typing import Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class LocalWhisperService:
    """
    Service for local Whisper speech-to-text transcription

    This service runs OpenAI's Whisper model locally, providing completely
    free audio transcription without any API costs.

    Attributes:
        model_name (str): Whisper model to use (tiny, base, small, medium, large)
        model: Loaded Whisper model instance
    """

    def __init__(self, model_name: str = "base"):
        """
        Initialize local Whisper service

        Args:
            model_name (str): Model size to use. Options:
                - "tiny": Fastest, 75MB (~39M parameters)
                - "base": Recommended, 142MB (~74M parameters)
                - "small": Better quality, 466MB (~244M parameters)
                - "medium": High quality, 1.5GB (~769M parameters)
                - "large": Best quality, 2.9GB (~1550M parameters)

        Note:
            On first run, the model will be downloaded to ~/.cache/whisper/
            This is a one-time download and will be reused for future runs.
        """
        self.model_name = model_name
        logger.info(f"Loading Whisper model '{model_name}' (this may take a moment on first run)...")

        try:
            # Load model (will download on first run)
            self.model = whisper.load_model(model_name)
            logger.info(f"✅ Whisper model '{model_name}' loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {str(e)}")
            raise

    async def transcribe_audio(self, audio_content: bytes, filename: str = "audio.wav") -> Dict:
        """
        Transcribe audio content to text using local Whisper model

        This method runs Whisper inference on the local machine, providing
        completely free transcription without any API costs.

        Args:
            audio_content (bytes): Audio file content as bytes
            filename (str): Original filename (used for file extension)

        Returns:
            dict: Transcription result with structure:
                {
                    "text": str,           # Transcribed text
                    "confidence": str,     # HIGH, MEDIUM, or LOW
                    "success": bool,       # True if successful
                    "language": str,       # Detected language (optional)
                    "duration": float      # Audio duration in seconds (optional)
                }

        Example:
            >>> service = LocalWhisperService(model_name="base")
            >>> audio_bytes = open("recording.mp3", "rb").read()
            >>> result = await service.transcribe_audio(audio_bytes, "recording.mp3")
            >>> print(result["text"])
            "Add new heifer, ear tag 12345, born January 15th 2024..."

        Performance:
            - Tiny model: ~5-10 seconds
            - Base model: ~10-20 seconds (RECOMMENDED)
            - Small model: ~20-40 seconds
            - Medium model: ~40-60 seconds
            - Large model: ~60-120 seconds

        Note:
            Transcription runs in a separate thread to avoid blocking the
            async event loop. This allows other requests to be processed
            while Whisper is working.
        """
        try:
            # Determine file extension from filename
            file_extension = os.path.splitext(filename)[1] or '.wav'

            # Create temporary file for Whisper to read
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(audio_content)
                temp_file_path = temp_file.name

            try:
                logger.info(f"Starting local Whisper transcription for {filename} using {self.model_name} model...")

                # Run transcription in thread pool to avoid blocking
                # Whisper is CPU-bound, so we use run_in_executor
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,  # Use default executor
                    self._transcribe_sync,
                    temp_file_path
                )

                # Extract transcription text
                transcription_text = result["text"].strip()

                # Determine confidence based on result quality
                # Whisper doesn't provide direct confidence scores, so we use heuristics
                confidence = self._estimate_confidence(result)

                # Get detected language (if available)
                detected_language = result.get("language", "unknown")

                logger.info(f"✅ Local transcription successful ({len(transcription_text)} chars, language: {detected_language})")
                logger.info(f"Preview: {transcription_text[:100]}...")

                return {
                    "text": transcription_text,
                    "confidence": confidence,
                    "success": True,
                    "language": detected_language,
                    "duration": result.get("duration"),
                    "model": self.model_name
                }

            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"❌ Error during local Whisper transcription: {str(e)}")
            return {
                "text": "",
                "confidence": "LOW",
                "success": False,
                "error": str(e)
            }

    def _transcribe_sync(self, audio_path: str) -> Dict:
        """
        Synchronous transcription (runs in thread pool)

        Args:
            audio_path (str): Path to temporary audio file

        Returns:
            dict: Whisper result with text, language, and metadata
        """
        # Run Whisper transcription
        # verbose=False suppresses progress output
        result = self.model.transcribe(audio_path, verbose=False)
        return result

    def _estimate_confidence(self, result: Dict) -> str:
        """
        Estimate confidence level based on Whisper result

        Whisper doesn't provide direct confidence scores, so we use heuristics:
        - Text length
        - Presence of punctuation
        - No probability available in result

        Args:
            result (dict): Whisper transcription result

        Returns:
            str: "HIGH", "MEDIUM", or "LOW"
        """
        text = result.get("text", "").strip()

        if not text:
            return "LOW"

        # Basic heuristics
        if len(text) < 10:
            return "MEDIUM"  # Very short transcriptions might be uncertain

        if len(text) > 20:
            return "HIGH"  # Longer transcriptions are generally more reliable

        return "MEDIUM"

    async def transcribe_audio_with_language(
        self,
        audio_content: bytes,
        language: str = "en",
        filename: str = "audio.wav"
    ) -> Dict:
        """
        Transcribe audio with specified language hint

        Args:
            audio_content (bytes): Audio file content
            language (str): ISO 639-1 language code (e.g., 'en', 'es', 'fr')
            filename (str): Original filename

        Returns:
            dict: Transcription result
        """
        try:
            file_extension = os.path.splitext(filename)[1] or '.wav'

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(audio_content)
                temp_file_path = temp_file.name

            try:
                logger.info(f"Starting transcription with language={language}")

                # Run with language parameter
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self.model.transcribe(temp_file_path, language=language, verbose=False)
                )

                transcription_text = result["text"].strip()
                confidence = self._estimate_confidence(result)

                logger.info(f"✅ Transcription successful (language: {language}): {transcription_text[:100]}...")

                return {
                    "text": transcription_text,
                    "confidence": confidence,
                    "success": True,
                    "language": language,
                    "model": self.model_name
                }

            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"❌ Error during transcription with language: {str(e)}")
            return {
                "text": "",
                "confidence": "LOW",
                "success": False,
                "error": str(e)
            }


# Convenience function for quick transcription
async def transcribe_file(audio_path: str, model_name: str = "base") -> str:
    """
    Quick transcription of a local audio file

    Args:
        audio_path (str): Path to audio file
        model_name (str): Whisper model to use

    Returns:
        str: Transcribed text

    Example:
        >>> text = await transcribe_file("recording.mp3", model_name="base")
        >>> print(text)
    """
    with open(audio_path, "rb") as f:
        audio_content = f.read()

    service = LocalWhisperService(model_name=model_name)
    result = await service.transcribe_audio(audio_content, audio_path)

    return result.get("text", "")
