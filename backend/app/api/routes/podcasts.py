import asyncio
import json
import os
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select

from app.models.database import async_session
from app.models.podcast import Podcast
from app.models.schemas import GenerateRequest, GenerateResponse, JobStatus, PodcastResponse
from app.services.job_manager import job_manager
from app.services.pipeline import run_pipeline

router = APIRouter(prefix="/api/podcasts", tags=["podcasts"])


@router.post("/generate", response_model=GenerateResponse, status_code=202)
async def generate_podcast(request: GenerateRequest):
    podcast_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())

    podcast = Podcast(
        id=podcast_id,
        title=request.title,
        document_ids=json.dumps([d for d in request.document_ids]),
        provider_id=request.provider_id,
        speakers=json.dumps([s.model_dump() for s in request.speakers]),
        language=request.language,

        num_speakers=len(request.speakers),
    )

    async with async_session() as session:
        session.add(podcast)
        await session.commit()

    job_manager.create_job(job_id, podcast_id)

    # Launch pipeline as background task
    asyncio.create_task(run_pipeline(job_id, podcast_id))

    return GenerateResponse(job_id=job_id, podcast_id=podcast_id)


@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(
        job_id=job.id,
        podcast_id=job.podcast_id,
        stage=job.stage.value,
        progress=job.progress,
        error=job.error,
    )


@router.get("", response_model=list[PodcastResponse])
async def list_podcasts():
    async with async_session() as session:
        result = await session.execute(select(Podcast).order_by(Podcast.created_at.desc()))
        podcasts = result.scalars().all()
    return [
        PodcastResponse(
            id=p.id,
            title=p.title,
            summary=p.summary,
            provider_id=p.provider_id,
            num_speakers=p.num_speakers,
            duration_seconds=p.duration_seconds,
            audio_path=p.audio_path,
            podbean_episode_id=p.podbean_episode_id,
            created_at=p.created_at,
        )
        for p in podcasts
    ]


@router.get("/{podcast_id}", response_model=PodcastResponse)
async def get_podcast(podcast_id: str):
    async with async_session() as session:
        result = await session.execute(select(Podcast).where(Podcast.id == podcast_id))
        podcast = result.scalar_one_or_none()
    if not podcast:
        raise HTTPException(status_code=404, detail="Podcast not found")
    return PodcastResponse(
        id=podcast.id,
        title=podcast.title,
        summary=podcast.summary,
        provider_id=podcast.provider_id,
        num_speakers=podcast.num_speakers,
        duration_seconds=podcast.duration_seconds,
        audio_path=podcast.audio_path,
        podbean_episode_id=podcast.podbean_episode_id,
        created_at=podcast.created_at,
    )


@router.get("/{podcast_id}/audio")
async def get_podcast_audio(podcast_id: str):
    async with async_session() as session:
        result = await session.execute(select(Podcast).where(Podcast.id == podcast_id))
        podcast = result.scalar_one_or_none()
    if not podcast or not podcast.audio_path:
        raise HTTPException(status_code=404, detail="Audio not found")
    if not os.path.exists(podcast.audio_path):
        raise HTTPException(status_code=404, detail="Audio file missing")
    media_type = "audio/wav" if podcast.audio_path.endswith(".wav") else "audio/mpeg"
    ext = "wav" if podcast.audio_path.endswith(".wav") else "mp3"
    return FileResponse(podcast.audio_path, media_type=media_type, filename=f"{podcast.title}.{ext}")
