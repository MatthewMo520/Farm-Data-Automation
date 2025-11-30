"""
Azure Blob Storage Service
Handles file uploads and downloads from Azure Storage
"""
from azure.storage.blob.aio import BlobServiceClient
from backend.core.config import settings
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class AzureStorageService:
    """Service for interacting with Azure Blob Storage"""

    def __init__(self):
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME

    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        content_type: str = None
    ) -> str:
        """
        Upload a file to Azure Blob Storage

        Args:
            file_content: File content as bytes
            filename: Original filename
            content_type: MIME type of the file

        Returns:
            URL of the uploaded blob
        """
        try:
            # Create blob service client
            blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )

            # Generate unique blob name
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            blob_name = f"{timestamp}_{unique_id}_{filename}"

            # Get blob client
            blob_client = blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            # Upload file
            await blob_client.upload_blob(
                file_content,
                content_settings={
                    "content_type": content_type
                } if content_type else None,
                overwrite=True
            )

            # Get blob URL
            blob_url = blob_client.url

            logger.info(f"File uploaded successfully: {blob_name}")

            await blob_service_client.close()

            return blob_url

        except Exception as e:
            logger.error(f"Error uploading file to Azure Storage: {str(e)}")
            raise

    async def download_file(self, blob_url: str) -> bytes:
        """
        Download a file from Azure Blob Storage

        Args:
            blob_url: URL of the blob

        Returns:
            File content as bytes
        """
        try:
            # Extract blob name from URL
            blob_name = blob_url.split("/")[-1]

            # Create blob service client
            blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )

            # Get blob client
            blob_client = blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            # Download file
            stream = await blob_client.download_blob()
            file_content = await stream.readall()

            logger.info(f"File downloaded successfully: {blob_name}")

            await blob_service_client.close()

            return file_content

        except Exception as e:
            logger.error(f"Error downloading file from Azure Storage: {str(e)}")
            raise

    async def delete_file(self, blob_url: str) -> bool:
        """
        Delete a file from Azure Blob Storage

        Args:
            blob_url: URL of the blob

        Returns:
            True if successful
        """
        try:
            # Extract blob name from URL
            blob_name = blob_url.split("/")[-1]

            # Create blob service client
            blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )

            # Get blob client
            blob_client = blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            # Delete file
            await blob_client.delete_blob()

            logger.info(f"File deleted successfully: {blob_name}")

            await blob_service_client.close()

            return True

        except Exception as e:
            logger.error(f"Error deleting file from Azure Storage: {str(e)}")
            raise
