import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { listPodcasts } from '../api/client';
import type { PodcastInfo } from '../types';

export default function HistoryPage() {
  const [podcasts, setPodcasts] = useState<PodcastInfo[]>([]);

  useEffect(() => {
    listPodcasts().then(setPodcasts);
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Podcast History</h1>

      {podcasts.length === 0 ? (
        <p className="text-gray-500">No podcasts generated yet.</p>
      ) : (
        <div className="space-y-3">
          {podcasts.map((p) => (
            <Link
              key={p.id}
              to={`/preview/${p.id}`}
              className="block bg-white border rounded-lg p-4 hover:border-blue-300 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-gray-900">{p.title}</h3>
                  <p className="text-sm text-gray-500">
                    {p.provider_id} &middot; {p.num_speakers} speakers
                    {p.duration_seconds && ` \u00B7 ${Math.round(p.duration_seconds / 60)} min`}
                  </p>
                </div>
                <div className="text-sm">
                  {p.podbean_episode_id ? (
                    <span className="text-green-600">Published</span>
                  ) : p.audio_path ? (
                    <span className="text-blue-600">Ready</span>
                  ) : (
                    <span className="text-gray-400">Processing</span>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
