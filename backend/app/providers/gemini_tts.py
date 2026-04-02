import io
import wave

import lameenc
from google import genai
from google.genai import types

from app.config import settings
from app.providers.base import AudioSegment, ScriptLine, TTSProvider

GEMINI_VOICES = [
    {"id": "Kore", "name": "Kore", "gender": "female"},
    {"id": "Charon", "name": "Charon", "gender": "male"},
    {"id": "Puck", "name": "Puck", "gender": "male"},
    {"id": "Aoede", "name": "Aoede", "gender": "female"},
    {"id": "Fenrir", "name": "Fenrir", "gender": "male"},
    {"id": "Leda", "name": "Leda", "gender": "female"},
]

WORDS_PER_MINUTE = 150
MAX_CHUNK_SECONDS = 580


def _estimate_duration_seconds(text: str) -> float:
    word_count = len(text.split())
    return (word_count / WORDS_PER_MINUTE) * 60


def _chunk_lines(lines: list[ScriptLine]) -> list[list[ScriptLine]]:
    chunks: list[list[ScriptLine]] = []
    current_chunk: list[ScriptLine] = []
    current_duration = 0.0

    for line in lines:
        line_duration = _estimate_duration_seconds(line.text)
        if current_duration + line_duration > MAX_CHUNK_SECONDS and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_duration = 0.0
        current_chunk.append(line)
        current_duration += line_duration

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _build_multi_speaker_prompt(lines: list[ScriptLine]) -> str:
    parts = []
    for line in lines:
        parts.append(f"{line.speaker}: {line.text}")
    return "\n\n".join(parts)


def _pcm_to_mp3(pcm_data: bytes, sample_rate: int = 24000, channels: int = 1, sample_width: int = 2) -> bytes:
    """Convert raw PCM data to MP3 using lameenc."""
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(128)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(channels)
    encoder.set_quality(2)
    mp3_data = encoder.encode(pcm_data)
    mp3_data += encoder.flush()
    return mp3_data


class GeminiTTSProvider(TTSProvider):
    def __init__(self):
        self._client = genai.Client(api_key=settings.gemini_api_key)

    async def synthesize(
        self,
        lines: list[ScriptLine],
        voice_map: dict[str, str],
    ) -> list[AudioSegment]:
        chunks = _chunk_lines(lines)
        all_segments: list[AudioSegment] = []

        speakers = list(voice_map.keys())
        voice_names = [voice_map.get(s, GEMINI_VOICES[i % len(GEMINI_VOICES)]["id"]) for i, s in enumerate(speakers)]

        for chunk in chunks:
            prompt = _build_multi_speaker_prompt(chunk)

            # Gemini multi-speaker TTS requires exactly 2 speakers
            if len(speakers) == 2:
                speaker_voice_configs = [
                    types.SpeakerVoiceConfig(
                        speaker=s,
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=v)
                        ),
                    )
                    for s, v in zip(speakers, voice_names)
                ]
                speech_config = types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=speaker_voice_configs
                    )
                )
            elif len(speakers) == 1:
                speech_config = types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_names[0] if voice_names else "Kore"
                        )
                    )
                )
            else:
                # 3+ speakers: map to 2 Gemini voices (host voice + guest voice)
                # First speaker gets voice 1, all others share voice 2
                speaker_voice_configs = [
                    types.SpeakerVoiceConfig(
                        speaker=speakers[0],
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_names[0])
                        ),
                    ),
                    types.SpeakerVoiceConfig(
                        speaker=speakers[1],
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_names[1])
                        ),
                    ),
                ]
                # Rewrite 3rd+ speakers as speaker[1] in the prompt
                remapped = []
                for line in chunk:
                    if line.speaker not in (speakers[0], speakers[1]):
                        remapped.append(ScriptLine(speaker=speakers[1], text=f"[{line.speaker}] {line.text}"))
                    else:
                        remapped.append(line)
                prompt = _build_multi_speaker_prompt(remapped)

                speech_config = types.SpeechConfig(
                    multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                        speaker_voice_configs=speaker_voice_configs
                    )
                )

            response = self._client.models.generate_content(
                model=settings.gemini_tts_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=speech_config,
                ),
            )

            audio_data = response.candidates[0].content.parts[0].inline_data.data
            mp3_bytes = _pcm_to_mp3(audio_data, sample_rate=24000)

            duration = _estimate_duration_seconds(
                " ".join(line.text for line in chunk)
            )

            all_segments.append(
                AudioSegment(
                    speaker="multi",
                    audio_data=mp3_bytes,
                    format="mp3",
                    duration_seconds=duration,
                )
            )

        return all_segments

    async def list_voices(self, language: str = "en") -> list[dict]:
        return GEMINI_VOICES
