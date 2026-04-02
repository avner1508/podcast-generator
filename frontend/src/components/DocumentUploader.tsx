import { useCallback, useState } from 'react';
import { deleteDocument, uploadDocument } from '../api/client';
import type { DocumentInfo } from '../types';

interface Props {
  documents: DocumentInfo[];
  onDocumentsChange: (docs: DocumentInfo[]) => void;
}

export default function DocumentUploader({ documents, onDocumentsChange }: Props) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFiles = useCallback(
    async (files: FileList) => {
      setError(null);
      setUploading(true);
      try {
        const uploaded: DocumentInfo[] = [];
        for (const file of Array.from(files)) {
          const doc = await uploadDocument(file);
          uploaded.push(doc);
        }
        onDocumentsChange([...documents, ...uploaded]);
      } catch (e: any) {
        setError(e.response?.data?.detail || 'Upload failed');
      } finally {
        setUploading(false);
      }
    },
    [documents, onDocumentsChange]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
      }
    },
    [handleFiles]
  );

  const handleRemove = async (id: string) => {
    try {
      await deleteDocument(id);
      onDocumentsChange(documents.filter((d) => d.id !== id));
    } catch {
      // ignore
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-medium text-gray-900">Documents</h2>

      <div
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
        }`}
      >
        <p className="text-gray-500 mb-2">Drag and drop PDF, TXT, or MD files here</p>
        <label className="inline-block px-4 py-2 bg-blue-600 text-white rounded cursor-pointer hover:bg-blue-700">
          {uploading ? 'Uploading...' : 'Browse Files'}
          <input
            type="file"
            className="hidden"
            multiple
            accept=".pdf,.txt,.md"
            onChange={(e) => e.target.files && handleFiles(e.target.files)}
            disabled={uploading}
          />
        </label>
      </div>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      {documents.length > 0 && (
        <ul className="space-y-2">
          {documents.map((doc) => (
            <li key={doc.id} className="flex items-center justify-between bg-white p-3 rounded border">
              <div>
                <span className="font-medium text-gray-900">{doc.filename}</span>
                <p className="text-sm text-gray-500 truncate max-w-md">{doc.text_preview}</p>
              </div>
              <button
                onClick={() => handleRemove(doc.id)}
                className="text-red-500 hover:text-red-700 text-sm"
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
