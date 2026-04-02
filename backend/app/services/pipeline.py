import json
import logging
import os

from sqlalchemy import select

logger = logging.getLogger(__name__)

from app.config import settings
from app.models.database import async_session
from app.models.document import Document
from app.models.podcast import Podcast
from app.providers.base import Script
from app.providers.registry import create_providers
from app.services.audio_assembler import assemble_audio
from app.services.document_parser import extract_text

async def _generate_summary(provider_id: str, script: Script, language: str = "en") -> str:
    """Generate a 300-char summary using the same LLM provider."""
    dialogue = "\n".join(f"{l.speaker}: {l.text}" for l in script.lines[:30])
    lang_instruction = f" Write the summary in the same language as the conversation." if language != "en" else ""
    prompt = (
        "Summarize this podcast conversation in one paragraph of 300 characters or fewer. "
        f"Output ONLY the summary, no quotes or labels.{lang_instruction}\n\n" + dialogue
    )

    try:
        if provider_id == "gemini_full":
            from google import genai
            client = genai.Client(api_key=settings.gemini_api_key)
            response = client.models.generate_content(
                model=settings.gemini_script_model,
                contents=prompt,
            )
            return response.text.strip()[:300]
        else:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
            response = await client.messages.create(
                model=settings.claude_script_model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()[:300]
    except Exception as e:
        logger.warning(f"Summary generation failed: {e}")
        return " ".join(l.text for l in script.lines[:3])[:300]
from app.services.job_manager import JobStage, job_manager


async def run_pipeline(job_id: str, podcast_id: str):
    """Execute the full podcast generation pipeline."""
    try:
        # Load podcast config
        async with async_session() as session:
            result = await session.execute(select(Podcast).where(Podcast.id == podcast_id))
            podcast = result.scalar_one()

        document_ids = json.loads(podcast.document_ids)
        speakers = json.loads(podcast.speakers)
        provider_id = podcast.provider_id
        language = getattr(podcast, "language", "en") or "en"

        # Stage 1: Parse documents
        logger.info(f"[{job_id[:8]}] Stage 1: Parsing documents...")
        await job_manager.update_job(job_id, JobStage.PARSING, 0.1)

        document_texts = []
        async with async_session() as session:
            for doc_id in document_ids:
                result = await session.execute(select(Document).where(Document.id == doc_id))
                doc = result.scalar_one_or_none()
                if doc:
                    document_texts.append(doc.extracted_text)

        combined_text = "\n\n---\n\n".join(document_texts)
        await job_manager.update_job(job_id, JobStage.PARSING, 0.2)

        # Stage 2: Generate script
        logger.info(f"[{job_id[:8]}] Stage 2: Generating script with {provider_id}...")
        await job_manager.update_job(job_id, JobStage.GENERATING_SCRIPT, 0.25)

        script_provider, tts_provider = create_providers(provider_id)
        language_instruction = None
        if language != "en":
            LANG_NAMES = {
                "he": "Hebrew", "es": "Spanish", "fr": "French", "de": "German",
                "it": "Italian", "pt": "Portuguese", "ar": "Arabic", "ru": "Russian",
                "ja": "Japanese", "ko": "Korean", "zh": "Chinese",
            }
            lang_name = LANG_NAMES.get(language, language)
            language_instruction = f"Write the entire podcast conversation in {lang_name}."

        script = await script_provider.generate_script(combined_text, speakers, language_instruction)

        # Generate summary (max 300 chars)
        logger.info(f"[{job_id[:8]}] Generating summary...")
        summary = await _generate_summary(provider_id, script, language)

        # Save script and summary to podcast
        script_json = json.dumps([{"speaker": l.speaker, "text": l.text} for l in script.lines])
        async with async_session() as session:
            result = await session.execute(select(Podcast).where(Podcast.id == podcast_id))
            podcast = result.scalar_one()
            podcast.script = script_json
            podcast.summary = summary
            await session.commit()

        logger.info(f"[{job_id[:8]}] Script generated: {len(script.lines)} lines")
        await job_manager.update_job(job_id, JobStage.GENERATING_SCRIPT, 0.5)

        # Stage 3: Generate audio
        logger.info(f"[{job_id[:8]}] Stage 3: Generating audio...")
        await job_manager.update_job(job_id, JobStage.GENERATING_AUDIO, 0.55)

        # Build voice map from speaker config, matching gender
        voice_map = {}
        voices = await tts_provider.list_voices(language=language)
        male_voices = [v for v in voices if v.get("gender") == "male"]
        female_voices = [v for v in voices if v.get("gender") == "female"]

        for i, s in enumerate(speakers):
            if s.get("voice_id"):
                voice_map[s["name"]] = s["voice_id"]
            else:
                gender = s.get("gender", "male")
                if gender == "female" and female_voices:
                    voice_map[s["name"]] = female_voices[i % len(female_voices)]["id"]
                elif male_voices:
                    voice_map[s["name"]] = male_voices[i % len(male_voices)]["id"]
                else:
                    voice_map[s["name"]] = voices[i % len(voices)]["id"]

        audio_segments = await tts_provider.synthesize(script.lines, voice_map)
        await job_manager.update_job(job_id, JobStage.GENERATING_AUDIO, 0.8)

        logger.info(f"[{job_id[:8]}] Audio generated: {len(audio_segments)} segments")

        # Stage 4: Assemble audio
        logger.info(f"[{job_id[:8]}] Stage 4: Assembling audio...")
        await job_manager.update_job(job_id, JobStage.ASSEMBLING, 0.85)

        output_path = os.path.join(settings.output_dir, f"{podcast_id}.mp3")
        actual_path, duration = assemble_audio(audio_segments, output_path)
        output_path = actual_path

        # Update podcast with audio info
        async with async_session() as session:
            result = await session.execute(select(Podcast).where(Podcast.id == podcast_id))
            podcast = result.scalar_one()
            podcast.audio_path = output_path
            podcast.duration_seconds = duration
            await session.commit()

        logger.info(f"[{job_id[:8]}] DONE! Duration: {duration:.1f}s, path: {output_path}")
        await job_manager.update_job(job_id, JobStage.COMPLETED, 1.0)

    except Exception as e:
        logger.error(f"[{job_id[:8]}] FAILED: {e}", exc_info=True)
        await job_manager.update_job(job_id, JobStage.FAILED, 0.0, error=str(e))
