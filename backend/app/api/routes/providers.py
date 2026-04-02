from fastapi import APIRouter

from app.models.schemas import ProviderInfo

router = APIRouter(prefix="/api/providers", tags=["providers"])

PROVIDERS = [
    ProviderInfo(
        id="gemini_full",
        name="Gemini Full",
        description="Google Gemini for both script generation and multi-speaker TTS",
        script_engine="Gemini 2.5 Pro",
        tts_engine="Gemini TTS",
    ),
    ProviderInfo(
        id="claude_gemini",
        name="Claude + Gemini TTS",
        description="Claude for script writing, Gemini for voice synthesis",
        script_engine="Claude",
        tts_engine="Gemini TTS",
    ),
    ProviderInfo(
        id="claude_elevenlabs",
        name="Claude + ElevenLabs",
        description="Claude for script writing, ElevenLabs for premium voices",
        script_engine="Claude",
        tts_engine="ElevenLabs",
    ),
]


@router.get("", response_model=list[ProviderInfo])
async def list_providers():
    return PROVIDERS
