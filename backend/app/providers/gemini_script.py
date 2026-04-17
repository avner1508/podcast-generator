import asyncio
import json
import logging

from google import genai

from app.config import settings
from app.providers.base import Script, ScriptLine, ScriptProvider

logger = logging.getLogger(__name__)

MAX_RETRIES = 4
RETRY_BASE_DELAY = 5  # seconds

SYSTEM_PROMPT = """You are a podcast script writer. Given document content, create an engaging,
natural-sounding podcast conversation between the specified speakers.

Rules:
- Make it conversational, not a lecture. Speakers should react, ask questions, and build on each other's points.
- Include natural speech patterns: "you know", "right", "exactly", brief pauses, reactions.
- Cover the key points from the documents but make them accessible and interesting.
- Each speaker should have a distinct personality based on their role.
- The conversation should flow naturally with good transitions between topics.
- Aim for a conversation that would take about 8-12 minutes when spoken aloud.

Output ONLY valid JSON in this exact format:
{
  "lines": [
    {"speaker": "Speaker Name", "text": "What they say"},
    ...
  ]
}"""


class GeminiScriptProvider(ScriptProvider):
    def __init__(self):
        self._client = genai.Client(api_key=settings.gemini_api_key)

    async def generate_script(
        self,
        document_text: str,
        speakers: list[dict],
        instructions: str | None = None,
    ) -> Script:
        speaker_descriptions = "\n".join(
            f"- {s['name']} (role: {s.get('role', 'host')})" for s in speakers
        )

        user_prompt = f"""Speakers:
{speaker_descriptions}

{f"Additional instructions: {instructions}" if instructions else ""}

Document content:
{document_text[:100000]}"""

        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                response = self._client.models.generate_content(
                    model=settings.gemini_script_model,
                    contents=user_prompt,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.9,
                        response_mime_type="application/json",
                    ),
                )
                data = json.loads(response.text)
                lines = [ScriptLine(speaker=line["speaker"], text=line["text"]) for line in data["lines"]]
                return Script(lines=lines)
            except Exception as e:
                last_error = e
                error_str = str(e)
                if "503" in error_str or "UNAVAILABLE" in error_str or "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(f"Gemini script model unavailable (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    raise
        raise last_error
