# Podcast Generator - Backend

Python FastAPI backend that orchestrates document-to-podcast generation using AI providers.

## Tech Stack

- **FastAPI** - async web framework
- **SQLAlchemy** (async) + **aiosqlite** - ORM and SQLite database
- **Pydantic Settings** - configuration via `.env`

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env    # Fill in your API keys
```

## Running

```bash
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

The database is auto-created on startup via `create_all`. To reset the DB after schema changes, delete `podcast_generator.db`.

## Configuration

All config is in `.env` (see `.env.example`):

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `GEMINI_SCRIPT_MODEL` | Model for script generation (default: `gemini-2.5-pro`) |
| `GEMINI_TTS_MODEL` | Model for TTS (default: `gemini-2.5-flash-preview-tts`) |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key |
| `CLAUDE_SCRIPT_MODEL` | Claude model name |
| `ELEVENLABS_API_KEY` | ElevenLabs API key |
| `ELEVENLABS_MODEL` | ElevenLabs model (default: `eleven_multilingual_v2`) |
| `PODBEAN_CLIENT_ID` | Podbean OAuth client ID |
| `PODBEAN_CLIENT_SECRET` | Podbean OAuth client secret |
| `UPLOAD_DIR` | Where uploaded files go (default: `./uploads`) |
| `OUTPUT_DIR` | Where generated audio goes (default: `./output`) |
| `MAX_SPEAKERS` | Max speakers per podcast (default: `3`) |

## Project Structure

```
app/
  main.py              # FastAPI app, CORS, route mounting, startup
  config.py            # Settings loaded from .env via pydantic-settings
  api/
    routes/
      documents.py     # Upload, list, delete documents
      podcasts.py      # Generate podcast, get job status, list/get podcasts, stream audio
      providers.py     # List available AI provider combos
      publish.py       # Publish podcast to Podbean
    websocket.py       # WebSocket endpoint for real-time job progress
  models/
    database.py        # SQLAlchemy async engine + session setup
    document.py        # Document SQLAlchemy model
    podcast.py         # Podcast SQLAlchemy model
    schemas.py         # Pydantic request/response schemas
  providers/
    base.py            # Abstract base classes: ScriptProvider, TTSProvider
    registry.py        # Maps provider IDs to script+TTS class pairs
    gemini_script.py   # Gemini script generation
    claude_script.py   # Claude script generation
    gemini_tts.py      # Gemini multi-speaker TTS
    elevenlabs_tts.py  # ElevenLabs TTS
  services/
    pipeline.py        # End-to-end generation pipeline (orchestrator)
    job_manager.py     # In-memory job tracking with pub/sub for WebSocket
    document_parser.py # PDF/TXT/MD text extraction (via PyMuPDF)
    audio_assembler.py # Concatenates audio segments into final file
    podbean_service.py # Podbean OAuth + upload + episode creation
```

## API Endpoints

### Documents

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/documents/upload` | Upload a document (PDF, TXT, MD). Returns extracted text preview |
| `GET` | `/api/documents` | List all uploaded documents |
| `DELETE` | `/api/documents/{id}` | Delete a document and its file |

### Podcasts

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/podcasts/generate` | Start podcast generation. Returns `job_id` + `podcast_id` |
| `GET` | `/api/podcasts/jobs/{job_id}` | Poll job status (stage + progress) |
| `GET` | `/api/podcasts` | List all podcasts |
| `GET` | `/api/podcasts/{id}` | Get single podcast details |
| `GET` | `/api/podcasts/{id}/audio` | Stream the generated audio file |
| `POST` | `/api/podcasts/{id}/publish` | Publish to Podbean (draft by default) |

### Other

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/providers` | List available AI provider combinations |
| `WS` | `/api/ws/jobs/{job_id}` | WebSocket for real-time generation progress |
| `GET` | `/api/health` | Health check |

## Generation Pipeline

The core flow lives in `services/pipeline.py` and runs as a background task:

1. **Parse documents** - loads document texts from DB
2. **Generate script** - sends combined text + speaker config to the selected LLM (Gemini or Claude). The LLM returns a multi-speaker conversation script. If language is not English, it instructs the LLM to write in the target language
3. **Generate summary** - uses the same LLM to produce a 300-char summary of the conversation
4. **Generate audio** - maps speakers to voices by gender, then sends script lines to the TTS provider (Gemini TTS or ElevenLabs). Gemini TTS handles all lines in a single multi-speaker call; ElevenLabs synthesizes line-by-line
5. **Assemble audio** - concatenates audio segments into a single file (WAV concat or MP3 byte concat)
6. **Save** - stores audio path and duration in the podcast DB record

Progress is tracked via `JobManager`, an in-memory pub/sub system. Each stage updates the job's `stage` and `progress` (0.0-1.0). WebSocket clients and HTTP polling both read from this.

## AI Provider System

Three provider combinations are available, configured in `providers/registry.py`:

| ID | Script Engine | TTS Engine |
|---|---|---|
| `gemini_full` | Gemini | Gemini TTS |
| `claude_gemini` | Claude | Gemini TTS |
| `claude_elevenlabs` | Claude | ElevenLabs |

Both script providers implement `ScriptProvider.generate_script()` which takes document text, speaker list, and optional language instructions, and returns a `Script` (list of `ScriptLine` with speaker + text).

Both TTS providers implement `TTSProvider.synthesize()` which takes script lines and a voice map (speaker name -> voice ID), and returns `AudioSegment` objects with raw audio bytes.

## Podbean Publishing

`services/podbean_service.py` handles the 3-step Podbean API flow:
1. Get OAuth token (client credentials grant, cached until expiry)
2. Request a presigned upload URL and upload the audio file
3. Create the episode (as draft or published)

## Database

SQLite with two tables:
- **documents** - uploaded files with extracted text
- **podcasts** - generated podcasts with title, provider, speakers (JSON), language, script (JSON), audio path, duration, Podbean episode ID

Schema is auto-created on startup. For schema changes, delete `podcast_generator.db` and restart.
