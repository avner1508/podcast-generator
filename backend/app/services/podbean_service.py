import os
from datetime import datetime, timedelta, timezone

import httpx

from app.config import settings

PODBEAN_API_BASE = "https://api.podbean.com/v1"


class PodbeanService:
    def __init__(self):
        self._token: str | None = None
        self._token_expires: datetime | None = None
        self._client_id = settings.podbean_client_id
        self._client_secret = settings.podbean_client_secret

    async def _ensure_token(self) -> str:
        if self._token and self._token_expires and datetime.now(timezone.utc) < self._token_expires:
            return self._token

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PODBEAN_API_BASE}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
            )
            response.raise_for_status()
            data = response.json()

        self._token = data["access_token"]
        expires_in = data.get("expires_in", 86400)
        self._token_expires = datetime.now(timezone.utc) + timedelta(seconds=expires_in - 60)
        return self._token

    async def publish_episode(
        self,
        audio_path: str,
        title: str,
        description: str,
        as_draft: bool = True,
    ) -> str:
        """Upload audio and create an episode. Returns episode ID."""
        token = await self._ensure_token()
        file_size = os.path.getsize(audio_path)
        filename = os.path.basename(audio_path)

        async with httpx.AsyncClient() as client:
            # Step 1: Authorize upload
            auth_response = await client.get(
                f"{PODBEAN_API_BASE}/files/uploadAuthorize",
                params={
                    "access_token": token,
                    "filename": filename,
                    "filesize": file_size,
                    "content_type": "audio/mpeg",
                },
            )
            auth_response.raise_for_status()
            auth_data = auth_response.json()
            presigned_url = auth_data["presigned_url"]
            file_key = auth_data["file_key"]

            # Step 2: Upload to presigned URL
            with open(audio_path, "rb") as f:
                upload_response = await client.put(
                    presigned_url,
                    content=f.read(),
                    headers={"Content-Type": "audio/mpeg"},
                    timeout=300,
                )
                upload_response.raise_for_status()

            # Step 3: Create episode
            episode_response = await client.post(
                f"{PODBEAN_API_BASE}/episodes",
                data={
                    "access_token": token,
                    "title": title,
                    "content": description or title,
                    "status": "draft" if as_draft else "publish",
                    "type": "public",
                    "media_key": file_key,
                },
            )
            episode_response.raise_for_status()
            episode_data = episode_response.json()

        return episode_data["episode"]["id"]


podbean_service = PodbeanService()
