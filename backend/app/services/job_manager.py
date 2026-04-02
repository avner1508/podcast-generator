import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class JobStage(str, Enum):
    QUEUED = "queued"
    PARSING = "parsing"
    GENERATING_SCRIPT = "generating_script"
    GENERATING_AUDIO = "generating_audio"
    ASSEMBLING = "assembling"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    id: str
    podcast_id: str
    stage: JobStage = JobStage.QUEUED
    progress: float = 0.0
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class JobManager:
    def __init__(self):
        self._jobs: dict[str, Job] = {}
        self._listeners: dict[str, list[asyncio.Queue]] = {}

    def create_job(self, job_id: str, podcast_id: str) -> Job:
        job = Job(id=job_id, podcast_id=podcast_id)
        self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    async def update_job(self, job_id: str, stage: JobStage, progress: float, error: str | None = None):
        job = self._jobs.get(job_id)
        if not job:
            return
        job.stage = stage
        job.progress = progress
        job.error = error
        job.updated_at = datetime.now(timezone.utc)
        await self._notify(job_id, job)

    def subscribe(self, job_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._listeners.setdefault(job_id, []).append(queue)
        return queue

    def unsubscribe(self, job_id: str, queue: asyncio.Queue):
        listeners = self._listeners.get(job_id, [])
        if queue in listeners:
            listeners.remove(queue)

    async def _notify(self, job_id: str, job: Job):
        for queue in self._listeners.get(job_id, []):
            await queue.put({
                "job_id": job.id,
                "podcast_id": job.podcast_id,
                "stage": job.stage.value,
                "progress": job.progress,
                "error": job.error,
            })


job_manager = JobManager()
