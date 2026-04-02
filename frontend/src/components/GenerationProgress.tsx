import type { JobStatus } from '../types';

interface Props {
  status: JobStatus | null;
}

const STAGE_LABELS: Record<string, string> = {
  queued: 'Queued',
  parsing: 'Parsing documents...',
  generating_script: 'Generating podcast script...',
  generating_audio: 'Generating audio...',
  assembling: 'Assembling final audio...',
  completed: 'Complete!',
  failed: 'Failed',
};

export default function GenerationProgress({ status }: Props) {
  if (!status) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
        <p className="mt-4 text-gray-500">Connecting...</p>
      </div>
    );
  }

  const label = STAGE_LABELS[status.stage] || status.stage;
  const progress = Math.round(status.progress * 100);

  return (
    <div className="space-y-4">
      <div className="text-center">
        {status.stage === 'failed' ? (
          <div className="text-red-600 text-4xl mb-2">!</div>
        ) : status.stage === 'completed' ? (
          <div className="text-green-600 text-4xl mb-2">&#10003;</div>
        ) : (
          <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-2" />
        )}
        <p className="text-lg font-medium text-gray-900">{label}</p>
      </div>

      {status.stage !== 'failed' && status.stage !== 'completed' && (
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-blue-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {status.error && (
        <div className="bg-red-50 border border-red-200 rounded p-4">
          <p className="text-red-700 text-sm">{status.error}</p>
        </div>
      )}
    </div>
  );
}
