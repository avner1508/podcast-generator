import { useCallback, useEffect, useRef, useState } from 'react';
import { getJobStatus } from '../api/client';
import type { JobStatus } from '../types';

export function useGenerationStatus(jobId: string | null) {
  const [status, setStatus] = useState<JobStatus | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const cleanup = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!jobId) return;

    // Fetch initial status immediately
    getJobStatus(jobId)
      .then(setStatus)
      .catch((err) => {
        if (err.response?.status === 404) {
          setStatus({ job_id: jobId, podcast_id: '', stage: 'failed', progress: 0, error: 'Job not found. It may have been lost after a server restart.' });
        }
      });

    // Start polling as the primary mechanism (reliable)
    pollRef.current = setInterval(async () => {
      try {
        const data = await getJobStatus(jobId);
        setStatus(data);
        if (data.stage === 'completed' || data.stage === 'failed') {
          cleanup();
        }
      } catch (err: any) {
        if (err.response?.status === 404) {
          setStatus({ job_id: jobId, podcast_id: '', stage: 'failed', progress: 0, error: 'Job not found. It may have been lost after a server restart.' });
          cleanup();
        }
      }
    }, 2000);

    // Also try WebSocket for faster updates
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const ws = new WebSocket(`${protocol}//${window.location.host}/api/ws/jobs/${jobId}`);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'heartbeat') return;
        setStatus(data as JobStatus);
      };

      ws.onerror = () => {
        ws.close();
        wsRef.current = null;
      };

      ws.onclose = () => {
        wsRef.current = null;
      };
    } catch {
      // WebSocket failed, polling will handle it
    }

    return cleanup;
  }, [jobId, cleanup]);

  const isComplete = status?.stage === 'completed';
  const isFailed = status?.stage === 'failed';

  return { status, isComplete, isFailed };
}
