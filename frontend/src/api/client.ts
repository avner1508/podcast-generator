import axios from 'axios';
import type { DocumentInfo, GenerateRequest, GenerateResponse, JobStatus, PodcastInfo, ProviderInfo } from '../types';

const api = axios.create({ baseURL: '/api' });

export async function uploadDocument(file: File): Promise<DocumentInfo> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post<DocumentInfo>('/documents/upload', formData);
  return data;
}

export async function listDocuments(): Promise<DocumentInfo[]> {
  const { data } = await api.get<DocumentInfo[]>('/documents');
  return data;
}

export async function deleteDocument(id: string): Promise<void> {
  await api.delete(`/documents/${id}`);
}

export async function listProviders(): Promise<ProviderInfo[]> {
  const { data } = await api.get<ProviderInfo[]>('/providers');
  return data;
}

export async function generatePodcast(request: GenerateRequest): Promise<GenerateResponse> {
  const { data } = await api.post<GenerateResponse>('/podcasts/generate', request);
  return data;
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const { data } = await api.get<JobStatus>(`/podcasts/jobs/${jobId}`);
  return data;
}

export async function listPodcasts(): Promise<PodcastInfo[]> {
  const { data } = await api.get<PodcastInfo[]>('/podcasts');
  return data;
}

export async function getPodcast(id: string): Promise<PodcastInfo> {
  const { data } = await api.get<PodcastInfo>(`/podcasts/${id}`);
  return data;
}

export function getAudioUrl(podcastId: string): string {
  return `/api/podcasts/${podcastId}/audio`;
}

export async function publishPodcast(podcastId: string, description: string, asDraft: boolean = true): Promise<void> {
  await api.post(`/podcasts/${podcastId}/publish`, { description, as_draft: asDraft });
}
