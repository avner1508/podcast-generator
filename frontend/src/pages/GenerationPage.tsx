import { useEffect } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import GenerationProgress from '../components/GenerationProgress';
import { useGenerationStatus } from '../hooks/useGenerationStatus';

export default function GenerationPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [searchParams] = useSearchParams();
  const podcastId = searchParams.get('podcast');
  const navigate = useNavigate();
  const { status, isComplete } = useGenerationStatus(jobId ?? null);

  useEffect(() => {
    if (isComplete && podcastId) {
      const timer = setTimeout(() => navigate(`/preview/${podcastId}`), 1500);
      return () => clearTimeout(timer);
    }
  }, [isComplete, podcastId, navigate]);

  return (
    <div className="max-w-lg mx-auto py-12">
      <h1 className="text-2xl font-bold text-gray-900 text-center mb-8">Generating Podcast</h1>
      <GenerationProgress status={status} />
      {isComplete && (
        <p className="text-center text-gray-500 mt-4">Redirecting to preview...</p>
      )}
    </div>
  );
}
