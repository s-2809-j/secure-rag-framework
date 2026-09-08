import { useState } from 'react';
import axiosInstance from '../api/axiosInstance';
import type { UploadResponse } from '../types';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragging, setDragging] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    const MAX_MB = 10;
    if (file.size > MAX_MB * 1024 * 1024) {
      setError(`File is too large. Maximum size is ${MAX_MB} MB.`);
      return;
    }

    const ALLOWED_EXTS = ['.pdf', '.docx', '.txt', '.md'];
    if (!ALLOWED_EXTS.some(ext => file.name.toLowerCase().endsWith(ext))) {
      setError('Unsupported file type. Please upload a PDF, DOCX, TXT, or Markdown file.');
      return;
    }

    setError('');
    setResult(null);
    setLoading(true);

    const form = new FormData();
    form.append('file', file);

    try {
      const { data } = await axiosInstance.post<UploadResponse>(
        '/api/v1/documents/upload',
        form,
        { headers: { 'Content-Type': 'multipart/form-data' } },
      );
      setResult(data);
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 403) {
        setError('You do not have permission to upload documents.');
      } else if (status === 413 || status === 400) {
        setError('File was rejected by the server. Check the file size and type.');
      } else if (status === 502) {
        setError('AI service is temporarily unavailable. Please try again.');
      } else {
        setError('Upload failed. Please check the file and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  };

  const isSuccess = result?.data.status?.toUpperCase() === 'SUCCESS';

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-sentinel-light">Knowledge Upload</h1>
        <p className="text-sentinel-muted text-sm mt-1">
          Ingest a document into the Sentinel knowledge base for RAG retrieval.
        </p>
      </div>

      {/* Upload card */}
      <div className="glass-card p-6 mb-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Drop zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl px-6 py-10 text-center transition-all duration-200 cursor-pointer
              ${dragging
                ? 'border-sentinel-accent bg-sentinel-accent/5'
                : file
                  ? 'border-violet-500/50 bg-violet-500/5'
                  : 'border-sentinel-border/50 hover:border-sentinel-accent/40 hover:bg-sentinel-surface/40'
              }`}
            onClick={() => document.getElementById('upload-file-input')?.click()}
          >
            <input
              id="upload-file-input"
              type="file"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            {file ? (
              <div className="flex flex-col items-center gap-2">
                <svg className="w-10 h-10 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                <p className="text-sentinel-light font-medium">{file.name}</p>
                <p className="text-sentinel-muted text-xs">{(file.size / 1024).toFixed(1)} KB</p>
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); setFile(null); }}
                  className="text-sentinel-muted hover:text-sentinel-danger text-xs mt-1 transition-colors"
                >
                  Remove file
                </button>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <svg className="w-10 h-10 text-sentinel-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
                <p className="text-sentinel-text font-medium">Drop a document to ingest or click to browse</p>
                <p className="text-sentinel-muted text-xs">Supports PDF, DOCX, TXT, Markdown, and more</p>
              </div>
            )}
          </div>

          {error && (
            <div className="flex items-center gap-2 bg-sentinel-danger/10 border border-sentinel-danger/30 rounded-xl px-4 py-3 text-sentinel-danger text-sm">
              <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              {error}
            </div>
          )}

          <button
            id="upload-submit"
            type="submit"
            disabled={!file || loading}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="spinner w-4 h-4" />
                Ingesting document…
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                Ingest into Knowledge Base
              </>
            )}
          </button>
        </form>
      </div>

      {/* Results */}
      {result && (
        <div className="glass-card p-6 space-y-6 animate-slide-up">
          {/* Header */}
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-sentinel-light font-semibold text-lg">Ingestion Results</h2>
              <p className="text-sentinel-muted text-xs mt-0.5">
                Request ID: <span className="font-mono">{result.requestId}</span>
              </p>
            </div>
            <span className={`badge border ${isSuccess ? 'bg-sentinel-success/10 text-sentinel-success border-sentinel-success/30' : 'bg-sentinel-danger/10 text-sentinel-danger border-sentinel-danger/30'}`}>
              {isSuccess ? '✅ SUCCESS' : '❌ FAILED'}
            </span>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {[
              { label: 'Status', value: result.data.status },
              { label: 'Chunks', value: result.data.chunkCount.toString() },
              { label: 'Embeddings', value: result.data.embeddingCount.toString() },
            ].map(({ label, value }) => (
              <div key={label} className="bg-sentinel-dark/50 rounded-xl p-4 border border-sentinel-border/30 text-center">
                <p className="text-sentinel-muted text-xs uppercase tracking-wider mb-1">{label}</p>
                <p className="text-sentinel-light font-bold text-xl">{value}</p>
              </div>
            ))}
          </div>

          {/* Ingestion message */}
          <div className="bg-sentinel-dark/50 rounded-xl p-4 border border-sentinel-border/30">
            <p className="text-xs font-semibold text-sentinel-muted uppercase tracking-wider mb-2">
              Ingestion Message
            </p>
            <p className="text-sentinel-text text-sm">{result.data.ingestionMessage}</p>
          </div>

          <p className="text-sentinel-muted/50 text-[10px] text-right">
            {new Date(result.timestamp).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
}
