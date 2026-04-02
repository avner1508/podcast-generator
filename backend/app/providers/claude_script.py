import json

import anthropic

from app.config import settings
from app.providers.base import Script, ScriptLine, ScriptProvider

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


class ClaudeScriptProvider(ScriptProvider):
    def __init__(self):
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

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
{document_text[:150000]}"""

        response = await self._client.messages.create(
            model=settings.claude_script_model,
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )

        text = response.content[0].text
        # Extract JSON from the response (handle potential markdown wrapping)
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]

        data = json.loads(text.strip())
        lines = [ScriptLine(speaker=line["speaker"], text=line["text"]) for line in data["lines"]]
        return Script(lines=lines)
