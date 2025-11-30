"""
Microsoft Dynamics 365 Client
Handles authentication and CRUD operations with Dynamics 365 Web API
"""
import httpx
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DynamicsClient:
    """Client for interacting with Microsoft Dynamics 365"""

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        tenant_id: str
    ):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.access_token = None
        self.token_expires_at = None

    async def authenticate(self) -> str:
        """
        Authenticate with Azure AD and get access token

        Returns:
            Access token
        """
        try:
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": f"{self.base_url}/.default",
                "grant_type": "client_credentials"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(token_url, data=data)
                response.raise_for_status()

                token_data = response.json()
                self.access_token = token_data["access_token"]
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 300)

                logger.info("Successfully authenticated with Dynamics 365")

                return self.access_token

        except Exception as e:
            logger.error(f"Error authenticating with Dynamics 365: {str(e)}")
            raise

    async def _ensure_authenticated(self):
        """Ensure we have a valid access token"""
        if not self.access_token or not self.token_expires_at:
            await self.authenticate()
        elif datetime.utcnow() >= self.token_expires_at:
            await self.authenticate()

    async def create_record(
        self,
        entity_name: str,
        data: Dict
    ) -> Dict:
        """
        Create a new record in Dynamics 365

        Args:
            entity_name: Dynamics entity name (e.g., "accounts", "contacts")
            data: Record data as dictionary

        Returns:
            Created record with ID
        """
        try:
            await self._ensure_authenticated()

            url = f"{self.base_url}/api/data/v9.2/{entity_name}"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0",
                "Accept": "application/json",
                "Prefer": "return=representation"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()

                created_record = response.json()
                record_id = created_record.get("id") or response.headers.get("OData-EntityId", "").split("(")[-1].rstrip(")")

                logger.info(f"Successfully created {entity_name} record with ID: {record_id}")

                return {
                    "id": record_id,
                    "data": created_record
                }

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating record: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error creating record in Dynamics 365: {str(e)}")
            raise

    async def update_record(
        self,
        entity_name: str,
        record_id: str,
        data: Dict
    ) -> bool:
        """
        Update an existing record in Dynamics 365

        Args:
            entity_name: Dynamics entity name
            record_id: ID of the record to update
            data: Updated data

        Returns:
            True if successful
        """
        try:
            await self._ensure_authenticated()

            url = f"{self.base_url}/api/data/v9.2/{entity_name}({record_id})"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0"
            }

            async with httpx.AsyncClient() as client:
                response = await client.patch(url, json=data, headers=headers)
                response.raise_for_status()

                logger.info(f"Successfully updated {entity_name} record: {record_id}")

                return True

        except Exception as e:
            logger.error(f"Error updating record in Dynamics 365: {str(e)}")
            raise

    async def get_record(
        self,
        entity_name: str,
        record_id: str,
        select_fields: Optional[list] = None
    ) -> Dict:
        """
        Retrieve a record from Dynamics 365

        Args:
            entity_name: Dynamics entity name
            record_id: ID of the record
            select_fields: Optional list of fields to retrieve

        Returns:
            Record data
        """
        try:
            await self._ensure_authenticated()

            url = f"{self.base_url}/api/data/v9.2/{entity_name}({record_id})"

            if select_fields:
                url += f"?$select={','.join(select_fields)}"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0",
                "Accept": "application/json"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                return response.json()

        except Exception as e:
            logger.error(f"Error retrieving record from Dynamics 365: {str(e)}")
            raise

    async def query_records(
        self,
        entity_name: str,
        filter_query: Optional[str] = None,
        select_fields: Optional[list] = None,
        top: int = 100
    ) -> list:
        """
        Query records from Dynamics 365

        Args:
            entity_name: Dynamics entity name
            filter_query: OData filter query
            select_fields: Fields to select
            top: Maximum number of records

        Returns:
            List of records
        """
        try:
            await self._ensure_authenticated()

            url = f"{self.base_url}/api/data/v9.2/{entity_name}"
            params = []

            if filter_query:
                params.append(f"$filter={filter_query}")
            if select_fields:
                params.append(f"$select={','.join(select_fields)}")
            if top:
                params.append(f"$top={top}")

            if params:
                url += "?" + "&".join(params)

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0",
                "Accept": "application/json"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                result = response.json()
                return result.get("value", [])

        except Exception as e:
            logger.error(f"Error querying records from Dynamics 365: {str(e)}")
            raise
