import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { generatePodcast } from '../api/client';
import DocumentUploader from '../components/DocumentUploader';
import ProviderSelector from '../components/ProviderSelector';
import SpeakerConfig from '../components/SpeakerConfig';
import type { DocumentInfo, Speaker } from '../types';

export default function HomePage() {
  const navigate = useNavigate();
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [providerId, setProviderId] = useState('gemini_full');
  const [speakers, setSpeakers] = useState<Speaker[]>([
    { name: 'Alex', role: 'host', gender: 'male', voice_id: '' },
    { name: 'Sam', role: 'expert', gender: 'female', voice_id: '' },
  ]);
  const [title, setTitle] = useState('');
  const [language, setLanguage] = useState('en');

  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canGenerate = documents.length > 0 && title.trim() && speakers.length > 0;

  const handleGenerate = async () => {
    if (!canGenerate) return;
    setGenerating(true);
    setError(null);
    try {
      const result = await generatePodcast({
        document_ids: documents.map((d) => d.id),
        provider_id: providerId,
        speakers,
        title: title.trim(),
        language,

      });
      navigate(`/generate/${result.job_id}?podcast=${result.podcast_id}`);
    } catch (e: any) {
      setError(e.response?.data?.detail || 'Generation failed');
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Create a Podcast</h1>
        <p className="text-gray-500 mt-1">Upload documents and generate a podcast conversation</p>
      </div>

      <DocumentUploader documents={documents} onDocumentsChange={setDocuments} />

      <ProviderSelector selected={providerId} onSelect={setProviderId} />

      <div className="space-y-2">
        <h2 className="text-lg font-medium text-gray-900">Language</h2>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="w-full px-4 py-3 border rounded-lg text-lg bg-white"
        >
          <option value="en">English</option>
          <option value="he">Hebrew (עברית)</option>
          <option value="es">Spanish (Español)</option>
          <option value="fr">French (Français)</option>
          <option value="de">German (Deutsch)</option>
          <option value="it">Italian (Italiano)</option>
          <option value="pt">Portuguese (Português)</option>
          <option value="ar">Arabic (العربية)</option>
          <option value="ru">Russian (Русский)</option>
          <option value="ja">Japanese (日本語)</option>
          <option value="ko">Korean (한국어)</option>
          <option value="zh">Chinese (中文)</option>
        </select>
      </div>

      <SpeakerConfig speakers={speakers} onSpeakersChange={setSpeakers} />

      <div className="space-y-2">
        <h2 className="text-lg font-medium text-gray-900">Episode Title</h2>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter podcast episode title"
          className="w-full px-4 py-3 border rounded-lg text-lg"
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      <button
        onClick={handleGenerate}
        disabled={!canGenerate || generating}
        className="w-full py-4 bg-blue-600 text-white text-lg font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {generating ? 'Starting generation...' : 'Generate Podcast'}
      </button>
    </div>
  );
}
