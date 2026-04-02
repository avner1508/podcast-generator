export interface Speaker {
  name: string;
  role: string;
  gender: string;
  voice_id: string;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  content_type: string;
  text_preview: string;
  created_at: string;
}

export interface ProviderInfo {
  id: string;
  name: string;
  description: string;
  script_engine: string;
  tts_engine: string;
}

export interface JobStatus {
  job_id: string;
  podcast_id: string;
  stage: string;
  progress: number;
  error: string | null;
}

export interface PodcastInfo {
  id: string;
  title: string;
  summary: string | null;
  provider_id: string;
  num_speakers: number;
  duration_seconds: number | null;
  audio_path: string | null;
  podbean_episode_id: string | null;
  created_at: string;
}

export interface GenerateRequest {
  document_ids: string[];
  provider_id: string;
  speakers: Speaker[];
  title: string;
  language: string;

}

export interface GenerateResponse {
  job_id: string;
  podcast_id: string;
}
