import type { Session } from '../api/client';

type Props = {
  sessions: Session[];
  currentId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
};

function formatDate(iso: string) {
  const d = new Date(iso);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  if (diff < 86400000) return 'Today';
  if (diff < 172800000) return 'Yesterday';
  return d.toLocaleDateString();
}

export function SessionList({ sessions, currentId, onSelect, onNew }: Props) {
  return (
    <div className="w-64 shrink-0 border-r border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/50 flex flex-col">
      <div className="p-3 border-b border-slate-200 dark:border-slate-700">
        <button
          onClick={onNew}
          className="w-full rounded-xl py-2.5 px-3 text-sm font-medium text-white bg-indigo-500 hover:bg-indigo-600 flex items-center justify-center gap-2 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
          </svg>
          New chat
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-2">
        <p className="px-3 py-2 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
          Recent
        </p>
        {sessions.length === 0 ? (
          <p className="px-3 py-4 text-sm text-slate-500 dark:text-slate-400">No chats yet</p>
        ) : (
          <ul className="space-y-0.5">
            {sessions.map((s) => (
              <li key={s.id}>
                <button
                  onClick={() => onSelect(s.id)}
                  className={`w-full text-left rounded-xl px-3 py-2.5 text-sm truncate transition-colors ${
                    s.id === currentId
                      ? 'bg-indigo-500/10 dark:bg-indigo-400/10 text-indigo-700 dark:text-indigo-300 font-medium'
                      : 'text-slate-700 dark:text-slate-300 hover:bg-slate-200/80 dark:hover:bg-slate-700/80'
                  }`}
                >
                  <span className="block truncate">{s.title || 'New build'}</span>
                  <span className="block text-xs text-slate-400 dark:text-slate-500 mt-0.5">
                    {formatDate(s.updated_at)}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
