import asyncio
import io

from elevenlabs import AsyncElevenLabs

from app.config import settings
from app.providers.base import AudioSegment, ScriptLine, TTSProvider

# Concurrency limit for ElevenLabs API calls
MAX_CONCURRENT = 5


class ElevenLabsTTSProvider(TTSProvider):
    def __init__(self):
        self._client = AsyncElevenLabs(api_key=settings.elevenlabs_api_key)

    async def synthesize(
        self,
        lines: list[ScriptLine],
        voice_map: dict[str, str],
    ) -> list[AudioSegment]:
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        segments: list[AudioSegment | None] = [None] * len(lines)

        async def process_line(index: int, line: ScriptLine):
            async with semaphore:
                voice_id = voice_map.get(line.speaker)
                if not voice_id:
                    # Use a default voice
                    voices = await self.list_voices()
                    voice_id = voices[index % len(voices)]["id"]

                audio_iter = await self._client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=line.text,
                    model_id=settings.elevenlabs_model,
                    output_format="mp3_44100_128",
                )

                # Collect all audio chunks
                audio_bytes = b""
                async for chunk in audio_iter:
                    audio_bytes += chunk

                # Estimate duration from text
                words = len(line.text.split())
                duration = (words / 150) * 60

                segments[index] = AudioSegment(
                    speaker=line.speaker,
                    audio_data=audio_bytes,
                    format="mp3",
                    duration_seconds=duration,
                )

        tasks = [process_line(i, line) for i, line in enumerate(lines)]
        await asyncio.gather(*tasks)

        return [s for s in segments if s is not None]

    async def list_voices(self, language: str = "en") -> list[dict]:
        response = await self._client.voices.get_all()
        return [
            {
                "id": v.voice_id,
                "name": v.name,
                "gender": getattr(v.labels, "gender", "unknown") if v.labels else "unknown",
            }
            for v in response.voices[:20]
        ]
