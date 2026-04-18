import { useState } from 'react';
import { publishPodcast } from '../api/client';

interface Props {
  podcastId: string;
  alreadyPublished: boolean;
}

export default function PublishButton({ podcastId, alreadyPublished }: Props) {
  const [publishing, setPublishing] = useState(false);
  const [published, setPublished] = useState(alreadyPublished);
  const [error, setError] = useState<string | null>(null);
  const [description] = useState('');
  const [asDraft, setAsDraft] = useState(true);
  const [showForm, setShowForm] = useState(false);

  const handlePublish = async () => {
    setPublishing(true);
    setError(null);
    try {
      await publishPodcast(podcastId, description, asDraft);
      setPublished(true);
      setShowForm(false);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Publishing failed');
    } finally {
      setPublishing(false);
    }
  };

  if (published) {
    return (
      <div className="bg-green-50 border border-green-200 rounded p-4 text-green-700 flex items-center justify-between">
        <span>Uploaded to Podbean as {asDraft ? 'draft' : 'published'}</span>
        <a
          href="https://admin5.podbean.com/bboazst/episodes/list"
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 whitespace-nowrap ml-4"
        >
          View Episodes ↗
        </a>
      </div>
    );
  }

  if (!showForm) {
    return (
      <button
        onClick={() => setShowForm(true)}
        className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
      >
        Upload to Podbean
      </button>
    );
  }

  return (
    <div className="space-y-3 bg-white border rounded-lg p-4">
      <h3 className="font-medium text-gray-900">Upload to Podbean</h3>
      <label className="flex items-center gap-2 text-sm text-gray-700">
        <input
          type="checkbox"
          checked={asDraft}
          onChange={(e) => setAsDraft(e.target.checked)}
          className="rounded"
        />
        Upload as draft (review in Podbean before publishing)
      </label>
      <div className="flex gap-2">
        <button
          onClick={handlePublish}
          disabled={publishing}
          className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
        >
          {publishing ? 'Uploading...' : asDraft ? 'Upload as Draft' : 'Publish Now'}
        </button>
        <button
          onClick={() => setShowForm(false)}
          className="px-4 py-2 border rounded hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
      {error && <p className="text-red-600 text-sm">{error}</p>}
    </div>
  );
}
