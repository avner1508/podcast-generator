from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ScriptLine:
    speaker: str
    text: str


@dataclass
class Script:
    lines: list[ScriptLine]
    title: str = ""


@dataclass
class AudioSegment:
    speaker: str
    audio_data: bytes
    format: str  # "mp3", "wav", etc.
    duration_seconds: float


class ScriptProvider(ABC):
    @abstractmethod
    async def generate_script(
        self,
        document_text: str,
        speakers: list[dict],
        instructions: str | None = None,
    ) -> Script:
        ...


class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(
        self,
        lines: list[ScriptLine],
        voice_map: dict[str, str],
    ) -> list[AudioSegment]:
        ...

    @abstractmethod
    async def list_voices(self, language: str = "en") -> list[dict]:
        ...
