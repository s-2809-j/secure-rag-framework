import { useCallback, useEffect, useState } from 'react';
import axiosInstance from '../api/axiosInstance';
import AuditTable from '../components/AuditTable';
import type { AuditPageResponse } from '../types';

const PAGE_SIZE = 50;

export default function AuditPage() {
  const [data,    setData]    = useState<AuditPageResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');

  const fetchPage = useCallback(async (p: number) => {
    setLoading(true);
    setError('');
    try {
      const { data: res } = await axiosInstance.get<AuditPageResponse>('/api/v1/audit', {
        params: { page: p, size: PAGE_SIZE },
      });
      setData(res);
    } catch {
      setError('Failed to load audit logs. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPage(0);
  }, [fetchPage]);

  const totalPages    = data?.totalPages    ?? 0;
  const totalElements = data?.totalElements ?? 0;
  const currentPage   = data?.number        ?? 0;

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-sentinel-light">Audit Log</h1>
          <p className="text-sentinel-muted text-sm mt-1">
            All API activity across the Sentinel platform.
            {data && (
              <span className="ml-2 text-sentinel-accent font-medium">
                {totalElements.toLocaleString()} total entries
              </span>
            )}
          </p>
        </div>
        <button
          onClick={() => fetchPage(currentPage)}
          disabled={loading}
          className="btn-secondary flex items-center gap-2 px-4 py-2 text-sm"
        >
          {loading ? (
            <span className="spinner w-4 h-4" />
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          )}
          Refresh
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 bg-sentinel-danger/10 border border-sentinel-danger/30 rounded-xl px-4 py-3 text-sentinel-danger text-sm mb-6">
          <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          {error}
        </div>
      )}

      {/* Loading skeleton */}
      {loading && !data && (
        <div className="glass-card p-6">
          <div className="space-y-3">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-10 bg-sentinel-border/20 rounded-lg animate-pulse" />
            ))}
          </div>
        </div>
      )}

      {/* Table */}
      {data && (
        <div className="glass-card p-0 overflow-hidden">
          {loading && (
            <div className="absolute inset-0 bg-sentinel-dark/40 backdrop-blur-sm z-10 flex items-center justify-center rounded-2xl">
              <span className="spinner w-8 h-8 text-sentinel-accent" />
            </div>
          )}
          <AuditTable entries={data.content} />
        </div>
      )}

      {/* Pagination */}
      {data && totalPages > 1 && (
        <div className="flex items-center justify-between mt-6">
          <p className="text-sentinel-muted text-sm">
            Page <span className="text-sentinel-light font-medium">{currentPage + 1}</span> of{' '}
            <span className="text-sentinel-light font-medium">{totalPages}</span>
            <span className="ml-2">
              (showing {data.content.length} of {totalElements.toLocaleString()})
            </span>
          </p>
          <div className="flex items-center gap-2">
            <button
              id="audit-prev"
              onClick={() => fetchPage(currentPage - 1)}
              disabled={currentPage === 0 || loading}
              className="btn-secondary px-4 py-2 text-sm flex items-center gap-1.5"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Previous
            </button>
            <button
              id="audit-next"
              onClick={() => fetchPage(currentPage + 1)}
              disabled={currentPage >= totalPages - 1 || loading}
              className="btn-secondary px-4 py-2 text-sm flex items-center gap-1.5"
            >
              Next
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
