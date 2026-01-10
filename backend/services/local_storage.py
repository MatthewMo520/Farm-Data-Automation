"""
Local Filesystem Storage Service
Handles file uploads and downloads from local server storage
"""
import aiofiles
import os
from datetime import datetime
from pathlib import Path
import uuid
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)


class LocalStorageService:
    """Service for interacting with local filesystem storage"""

    def __init__(self):
        self.base_path = Path(settings.LOCAL_STORAGE_PATH)
        # Create base directory if it doesn't exist
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_storage_path(self, client_id: str, filename: str) -> Path:
        """
        Generate organized storage path for a file

        Args:
            client_id: Client/tenant ID
            filename: Original filename

        Returns:
            Path object for file storage location
        """
        # Organize by client_id and year-month
        year_month = datetime.utcnow().strftime("%Y-%m")

        # Generate unique filename with timestamp and UUID
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_extension = Path(filename).suffix
        unique_filename = f"{timestamp}_{unique_id}{file_extension}"

        # Full path: /storage/recordings/{client_id}/{year-month}/{unique_filename}
        file_path = self.base_path / str(client_id) / year_month / unique_filename

        # Create directory structure
        file_path.parent.mkdir(parents=True, exist_ok=True)

        return file_path

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        client_id: str,
        content_type: str = None
    ) -> str:
        """
        Upload a file to local filesystem

        Args:
            file_content: File content as bytes
            filename: Original filename
            client_id: Client ID for organization
            content_type: MIME type of the file (not used for local storage)

        Returns:
            Relative file path from base storage path
        """
        try:
            file_path = self._get_storage_path(client_id, filename)

            # Write file asynchronously
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)

            # Return relative path from base storage path
            relative_path = file_path.relative_to(self.base_path)

            logger.info(f"File uploaded successfully: {relative_path}")

            return str(relative_path)

        except Exception as e:
            logger.error(f"Error uploading file to local storage: {str(e)}")
            raise

    async def download_file(self, file_path: str) -> bytes:
        """
        Download a file from local filesystem

        Args:
            file_path: Relative path from base storage path

        Returns:
            File content as bytes
        """
        try:
            full_path = self.base_path / file_path

            if not full_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Read file asynchronously
            async with aiofiles.open(full_path, 'rb') as f:
                file_content = await f.read()

            logger.info(f"File downloaded successfully: {file_path}")

            return file_content

        except Exception as e:
            logger.error(f"Error downloading file from local storage: {str(e)}")
            raise

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from local filesystem

        Args:
            file_path: Relative path from base storage path

        Returns:
            True if successful
        """
        try:
            full_path = self.base_path / file_path

            if full_path.exists():
                # Delete file
                full_path.unlink()

                # Try to remove empty parent directories (cleanup)
                try:
                    full_path.parent.rmdir()  # Only works if empty
                except OSError:
                    pass  # Directory not empty, which is fine

                logger.info(f"File deleted successfully: {file_path}")
            else:
                logger.warning(f"File not found for deletion: {file_path}")

            return True

        except Exception as e:
            logger.error(f"Error deleting file from local storage: {str(e)}")
            raise

    def get_file_path(self, relative_path: str) -> str:
        """
        Get absolute file path from relative path

        Args:
            relative_path: Relative path from base storage

        Returns:
            Absolute file path as string
        """
        return str(self.base_path / relative_path)

    async def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists

        Args:
            file_path: Relative path from base storage path

        Returns:
            True if file exists
        """
        full_path = self.base_path / file_path
        return full_path.exists()

    def get_file_size(self, file_path: str) -> int:
        """
        Get file size in bytes

        Args:
            file_path: Relative path from base storage path

        Returns:
            File size in bytes
        """
        full_path = self.base_path / file_path
        if full_path.exists():
            return full_path.stat().st_size
        return 0
