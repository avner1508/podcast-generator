import { useEffect, useState } from 'react';
import { listProviders } from '../api/client';
import type { ProviderInfo } from '../types';

interface Props {
  selected: string;
  onSelect: (id: string) => void;
}

export default function ProviderSelector({ selected, onSelect }: Props) {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);

  useEffect(() => {
    listProviders().then(setProviders);
  }, []);

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-medium text-gray-900">AI Provider</h2>
      <div className="grid gap-3 sm:grid-cols-3">
        {providers.map((p) => (
          <button
            key={p.id}
            onClick={() => onSelect(p.id)}
            className={`p-4 rounded-lg border-2 text-left transition-colors ${
              selected === p.id
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="font-medium text-gray-900">{p.name}</div>
            <div className="text-sm text-gray-500 mt-1">{p.description}</div>
            <div className="text-xs text-gray-400 mt-2">
              Script: {p.script_engine} &middot; Voice: {p.tts_engine}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
