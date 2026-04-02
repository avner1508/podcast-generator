import io
import os
import wave

from app.providers.base import AudioSegment


def assemble_audio(segments: list[AudioSegment], output_path: str) -> tuple[str, float]:
    """Write audio segments to a file. Returns (actual_path, duration_seconds).

    For a single segment (most common case), just writes it directly.
    For multiple WAV segments, concatenates them using the wave module.
    For multiple MP3 segments, concatenates the raw bytes (valid for MP3).
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if len(segments) == 1:
        # Single segment — write directly, no processing needed
        ext = segments[0].format
        actual_path = output_path.rsplit(".", 1)[0] + f".{ext}"
        with open(actual_path, "wb") as f:
            f.write(segments[0].audio_data)
        return actual_path, segments[0].duration_seconds

    # Multiple segments — concatenate
    fmt = segments[0].format

    if fmt == "wav":
        actual_path = output_path.rsplit(".", 1)[0] + ".wav"
        _concat_wav(segments, actual_path)
    else:
        actual_path = output_path
        with open(actual_path, "wb") as f:
            for seg in segments:
                f.write(seg.audio_data)

    return actual_path, sum(s.duration_seconds for s in segments)


def _concat_wav(segments: list[AudioSegment], output_path: str):
    """Concatenate WAV segments using Python's wave module."""
    first = wave.open(io.BytesIO(segments[0].audio_data), "rb")
    params = first.getparams()
    first.close()

    with wave.open(output_path, "wb") as out:
        out.setparams(params)
        for seg in segments:
            with wave.open(io.BytesIO(seg.audio_data), "rb") as inp:
                out.writeframes(inp.readframes(inp.getnframes()))
