import type { Speaker } from '../types';

interface Props {
  speakers: Speaker[];
  onSpeakersChange: (speakers: Speaker[]) => void;
  maxSpeakers?: number;
}

const ROLES = ['host', 'expert', 'interviewer'];
const GENDERS = ['male', 'female'];

export default function SpeakerConfig({ speakers, onSpeakersChange, maxSpeakers = 3 }: Props) {
  const updateSpeaker = (index: number, field: keyof Speaker, value: string) => {
    const updated = [...speakers];
    updated[index] = { ...updated[index], [field]: value };
    onSpeakersChange(updated);
  };

  const addSpeaker = () => {
    if (speakers.length >= maxSpeakers) return;
    onSpeakersChange([...speakers, { name: `Speaker ${speakers.length + 1}`, role: 'host', gender: 'male', voice_id: '' }]);
  };

  const removeSpeaker = (index: number) => {
    if (speakers.length <= 1) return;
    onSpeakersChange(speakers.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium text-gray-900">Speakers ({speakers.length})</h2>
        {speakers.length < maxSpeakers && (
          <button onClick={addSpeaker} className="text-sm text-blue-600 hover:text-blue-800">
            + Add Speaker
          </button>
        )}
      </div>

      <div className="space-y-3">
        {speakers.map((speaker, i) => (
          <div key={i} className="flex gap-3 items-start bg-white p-4 rounded-lg border">
            <div className="flex-1 space-y-2">
              <input
                type="text"
                value={speaker.name}
                onChange={(e) => updateSpeaker(i, 'name', e.target.value)}
                placeholder="Speaker name"
                className="w-full px-3 py-2 border rounded text-sm"
              />
              <div className="flex gap-2">
                <select
                  value={speaker.role}
                  onChange={(e) => updateSpeaker(i, 'role', e.target.value)}
                  className="flex-1 px-3 py-2 border rounded text-sm"
                >
                  {ROLES.map((r) => (
                    <option key={r} value={r}>
                      {r.charAt(0).toUpperCase() + r.slice(1)}
                    </option>
                  ))}
                </select>
                <select
                  value={speaker.gender}
                  onChange={(e) => updateSpeaker(i, 'gender', e.target.value)}
                  className="flex-1 px-3 py-2 border rounded text-sm"
                >
                  {GENDERS.map((g) => (
                    <option key={g} value={g}>
                      {g.charAt(0).toUpperCase() + g.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            {speakers.length > 1 && (
              <button
                onClick={() => removeSpeaker(i)}
                className="text-red-500 hover:text-red-700 text-sm mt-2"
              >
                Remove
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
