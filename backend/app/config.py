from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Gemini
    gemini_api_key: str = ""
    gemini_script_model: str = "gemini-2.5-pro"
    gemini_tts_model: str = "gemini-2.5-flash-preview-tts"

    # Claude
    anthropic_api_key: str = ""
    claude_script_model: str = "claude-sonnet-4-20250514"

    # ElevenLabs
    elevenlabs_api_key: str = ""
    elevenlabs_model: str = "eleven_multilingual_v2"

    # Podbean
    podbean_client_id: str = ""
    podbean_client_secret: str = ""

    # App
    upload_dir: str = "./uploads"
    output_dir: str = "./output"
    max_speakers: int = 3
    gemini_tts_max_seconds: int = 655
    database_url: str = "sqlite+aiosqlite:///./podcast_generator.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
