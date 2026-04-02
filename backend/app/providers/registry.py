from dataclasses import dataclass

from app.providers.base import ScriptProvider, TTSProvider
from app.providers.claude_script import ClaudeScriptProvider
from app.providers.gemini_script import GeminiScriptProvider


@dataclass
class PipelineConfig:
    id: str
    name: str
    description: str
    script_provider_class: type[ScriptProvider]
    tts_provider_class: type[TTSProvider]


def _get_pipelines() -> dict[str, PipelineConfig]:
    # Lazy imports to avoid loading TTS providers until needed
    from app.providers.elevenlabs_tts import ElevenLabsTTSProvider
    from app.providers.gemini_tts import GeminiTTSProvider

    return {
        "gemini_full": PipelineConfig(
            id="gemini_full",
            name="Gemini Full",
            description="Gemini for script + Gemini TTS for voices",
            script_provider_class=GeminiScriptProvider,
            tts_provider_class=GeminiTTSProvider,
        ),
        "claude_gemini": PipelineConfig(
            id="claude_gemini",
            name="Claude + Gemini TTS",
            description="Claude for script + Gemini TTS for voices",
            script_provider_class=ClaudeScriptProvider,
            tts_provider_class=GeminiTTSProvider,
        ),
        "claude_elevenlabs": PipelineConfig(
            id="claude_elevenlabs",
            name="Claude + ElevenLabs",
            description="Claude for script + ElevenLabs for premium voices",
            script_provider_class=ClaudeScriptProvider,
            tts_provider_class=ElevenLabsTTSProvider,
        ),
    }


def get_pipeline(provider_id: str) -> PipelineConfig:
    pipelines = _get_pipelines()
    if provider_id not in pipelines:
        raise ValueError(f"Unknown provider: {provider_id}. Available: {list(pipelines.keys())}")
    return pipelines[provider_id]


def create_providers(provider_id: str) -> tuple[ScriptProvider, TTSProvider]:
    config = get_pipeline(provider_id)
    return config.script_provider_class(), config.tts_provider_class()
