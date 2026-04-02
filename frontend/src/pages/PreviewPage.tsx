import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getAudioUrl, getPodcast } from '../api/client';
import AudioPlayer from '../components/AudioPlayer';
import PublishButton from '../components/PublishButton';
import type { PodcastInfo } from '../types';

export default function PreviewPage() {
  const { podcastId } = useParams<{ podcastId: string }>();
  const [podcast, setPodcast] = useState<PodcastInfo | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!podcastId) return;
    getPodcast(podcastId)
      .then(setPodcast)
      .catch(() => setError('Could not load podcast'));
  }, [podcastId]);

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!podcast) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{podcast.title}</h1>
        <p className="text-gray-500 mt-1">
          {podcast.num_speakers} speakers &middot; Provider: {podcast.provider_id}
          {podcast.duration_seconds && ` \u00B7 ${Math.round(podcast.duration_seconds / 60)} min`}
        </p>
        {podcast.summary && (
          <div className="mt-3 bg-gray-100 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-1">Summary</h3>
            <p className="text-gray-600 text-sm">{podcast.summary}</p>
          </div>
        )}
      </div>

      {podcast.audio_path ? (
        <>
          <AudioPlayer src={getAudioUrl(podcast.id)} title={podcast.title} />
          <PublishButton
            podcastId={podcast.id}
            alreadyPublished={!!podcast.podbean_episode_id}
          />
        </>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded p-4">
          <p className="text-yellow-700">Audio is not ready yet.</p>
        </div>
      )}
    </div>
  );
}
