import type { AuditLog } from '../types';

interface AuditTableProps {
  entries: AuditLog[];
}

const STATUS_COLOR: Record<number, string> = {
  200: 'text-sentinel-success',
  201: 'text-sentinel-success',
  400: 'text-sentinel-warning',
  401: 'text-sentinel-danger',
  403: 'text-sentinel-danger',
  500: 'text-red-400',
};

function statusColor(code: number): string {
  return STATUS_COLOR[code] ?? (code < 300 ? 'text-sentinel-success' : code < 500 ? 'text-sentinel-warning' : 'text-sentinel-danger');
}

export default function AuditTable({ entries }: AuditTableProps) {
  if (entries.length === 0) {
    return (
      <div className="text-center py-16 text-sentinel-muted">
        No audit entries found.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-sentinel-border/40">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-sentinel-border/40 bg-sentinel-surface/40">
            {['ID', 'User', 'Action', 'Endpoint', 'Status', 'IP Address', 'Timestamp'].map((h) => (
              <th
                key={h}
                className="px-4 py-3 text-left font-semibold text-sentinel-muted text-xs uppercase tracking-wider whitespace-nowrap"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {entries.map((entry, idx) => (
            <tr
              key={`${entry.id}-${entry.timestamp}`}
              className={`border-b border-sentinel-border/20 transition-colors hover:bg-sentinel-surface/60
                ${idx % 2 === 0 ? 'bg-transparent' : 'bg-sentinel-surface/20'}`}
            >
              <td className="px-4 py-3 font-mono text-xs text-sentinel-muted">{entry.id}</td>
              <td className="px-4 py-3 text-sentinel-text">{entry.userId ?? '—'}</td>
              <td className="px-4 py-3">
                <span className="font-mono text-xs bg-sentinel-border/30 text-sentinel-accent px-2 py-0.5 rounded">
                  {entry.action}
                </span>
              </td>
              <td className="px-4 py-3 font-mono text-xs text-sentinel-muted max-w-[200px] truncate" title={entry.endpoint}>
                {entry.endpoint}
              </td>
              <td className={`px-4 py-3 font-mono font-bold ${statusColor(entry.statusCode)}`}>
                {entry.statusCode}
              </td>
              <td className="px-4 py-3 font-mono text-xs text-sentinel-muted">{entry.ipAddress}</td>
              <td className="px-4 py-3 text-xs text-sentinel-muted whitespace-nowrap">
                {new Date(entry.timestamp).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
