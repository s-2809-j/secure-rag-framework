import { useState } from 'react';
import axiosInstance from '../api/axiosInstance';
import type { AnalysisResponse } from '../types';

const RISK_STYLES: Record<string, { bar: string; badge: string; label: string }> = {
  LOW: { bar: 'bg-sentinel-success', badge: 'risk-low', label: '🟢 LOW' },
  MEDIUM: { bar: 'bg-sentinel-warning', badge: 'risk-medium', label: '🟡 MEDIUM' },
  HIGH: { bar: 'bg-sentinel-danger', badge: 'risk-high', label: '🔴 HIGH' },
  CRITICAL: { bar: 'bg-red-600', badge: 'risk-critical', label: '🚨 CRITICAL' },
};

function getRiskStyle(level: string) {
  return RISK_STYLES[level?.toUpperCase()] ?? RISK_STYLES['LOW'];
}

export default function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
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

    const ALLOWED_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown'];
    const ALLOWED_EXTS = ['.pdf', '.docx', '.txt', '.md'];
    const hasValidType = ALLOWED_TYPES.includes(file.type);
    const hasValidExt = ALLOWED_EXTS.some(ext => file.name.toLowerCase().endsWith(ext));
    if (!hasValidType && !hasValidExt) {
      setError('Unsupported file type. Please upload a PDF, DOCX, TXT, or Markdown file.');
      return;
    }

    setError('');
    setResult(null);
    setLoading(true);

    const form = new FormData();
    form.append('file', file);

    try {
      const { data } = await axiosInstance.post<AnalysisResponse>(
        '/api/v1/documents/analyze',
        form,
        { headers: { 'Content-Type': 'multipart/form-data' } },
      );
      setResult(data);
    } catch {
      setError('Analysis failed. Please check the file and try again.');
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

  const riskStyle = result ? getRiskStyle(result.data.riskLevel) : null;
  const scorePercent = result ? Math.round(result.data.riskScore * 100) : 0;

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-sentinel-light">Document Analysis</h1>
        <p className="text-sentinel-muted text-sm mt-1">
          Upload a document to scan for security risks using Sentinel's AI engine.
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
                  ? 'border-sentinel-success/50 bg-sentinel-success/5'
                  : 'border-sentinel-border/50 hover:border-sentinel-accent/40 hover:bg-sentinel-surface/40'
              }`}
            onClick={() => document.getElementById('analyze-file-input')?.click()}
          >
            <input
              id="analyze-file-input"
              type="file"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            {file ? (
              <div className="flex flex-col items-center gap-2">
                <svg className="w-10 h-10 text-sentinel-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
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
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-sentinel-text font-medium">Drop a file here or click to browse</p>
                <p className="text-sentinel-muted text-xs">Supports PDF, DOCX, TXT, and more</p>
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
            id="analyze-submit"
            type="submit"
            disabled={!file || loading}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="spinner w-4 h-4" />
                Analyzing document…
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                Run Security Analysis
              </>
            )}
          </button>
        </form>
      </div>

      {/* Results */}
      {result && riskStyle && (
        <div className="glass-card p-6 space-y-6 animate-slide-up">
          {/* Header */}
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-sentinel-light font-semibold text-lg">Analysis Results</h2>
              <p className="text-sentinel-muted text-xs mt-0.5">
                Request ID: <span className="font-mono">{result.requestId}</span>
              </p>
            </div>
            <span className={`badge border text-sm px-3 py-1 ${riskStyle.badge}`}>
              {riskStyle.label}
            </span>
          </div>

          {/* Risk score bar */}
          <div>
            <div className="flex justify-between text-xs text-sentinel-muted mb-2">
              <span>Risk Score</span>
              <span className="font-mono font-semibold text-sentinel-light">{scorePercent}%</span>
            </div>
            <div className="h-2.5 bg-sentinel-border/40 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-700 ${riskStyle.bar}`}
                style={{ width: `${scorePercent}%` }}
              />
            </div>
          </div>

          {/* Recommendation */}
          <div className="bg-sentinel-dark/50 rounded-xl p-4 border border-sentinel-border/30">
            <p className="text-xs font-semibold text-sentinel-muted uppercase tracking-wider mb-2">
              Recommendation
            </p>
            <p className="text-sentinel-text text-sm leading-relaxed">
              {result.data.recommendation}
            </p>
          </div>

          {/* Findings */}
          {result.data.findings && result.data.findings.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-sentinel-muted uppercase tracking-wider mb-3">
                Findings ({result.data.findings.length})
              </p>
              <ul className="space-y-2">
                {result.data.findings.map((f, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm text-sentinel-text bg-sentinel-dark/40 rounded-lg px-3 py-2"
                  >
                    <span className="text-sentinel-warning mt-0.5">▸</span>
                    <span>{typeof f === 'string' ? f : JSON.stringify(f)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.data.findings?.length === 0 && (
            <div className="flex items-center gap-2 text-sentinel-success text-sm">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              No findings detected.
            </div>
          )}

          <p className="text-sentinel-muted/50 text-[10px] text-right">
            {new Date(result.timestamp).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
}
