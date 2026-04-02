from datetime import datetime

from pydantic import BaseModel


class SpeakerConfig(BaseModel):
    name: str
    role: str = "host"  # host, expert, interviewer
    gender: str = "male"  # male, female
    voice_id: str = ""


class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    text_preview: str
    created_at: datetime


class GenerateRequest(BaseModel):
    document_ids: list[str]
    provider_id: str
    speakers: list[SpeakerConfig]
    title: str
    language: str = "en"  # Language code: en, he, es, fr, de, etc.



class GenerateResponse(BaseModel):
    job_id: str
    podcast_id: str


class JobStatus(BaseModel):
    job_id: str
    podcast_id: str
    stage: str
    progress: float
    error: str | None = None


class PodcastResponse(BaseModel):
    id: str
    title: str
    summary: str | None
    provider_id: str
    num_speakers: int
    duration_seconds: float | None
    audio_path: str | None
    podbean_episode_id: str | None
    created_at: datetime


class ProviderInfo(BaseModel):
    id: str
    name: str
    description: str
    script_engine: str
    tts_engine: str


class PublishRequest(BaseModel):
    description: str = ""
    as_draft: bool = True
