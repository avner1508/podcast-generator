from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.models.database import async_session
from app.models.podcast import Podcast
from app.models.schemas import PublishRequest
from app.services.podbean_service import podbean_service

router = APIRouter(prefix="/api/podcasts", tags=["publish"])


@router.post("/{podcast_id}/publish")
async def publish_podcast(podcast_id: str, request: PublishRequest):
    async with async_session() as session:
        result = await session.execute(select(Podcast).where(Podcast.id == podcast_id))
        podcast = result.scalar_one_or_none()

    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    if not podcast.audio_path:
        raise HTTPException(status_code=400, detail="Podcast has no audio yet")
    if podcast.podbean_episode_id:
        raise HTTPException(status_code=400, detail="Already published")

    try:
        episode_id = await podbean_service.publish_episode(
            audio_path=podcast.audio_path,
            title=podcast.title,
            description=request.description or podcast.summary or podcast.title,
            as_draft=request.as_draft,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Podbean publishing failed: {e}")

    async with async_session() as session:
        result = await session.execute(select(Podcast).where(Podcast.id == podcast_id))
        podcast = result.scalar_one()
        podcast.podbean_episode_id = episode_id
        await session.commit()

    status = "draft" if request.as_draft else "published"
    return {"status": status, "episode_id": episode_id}
