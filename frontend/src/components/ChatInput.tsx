import { useState } from 'react';

type Props = {
  onSend: (message: string) => void;
  disabled?: boolean;
};

export function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (trimmed && !disabled) {
      onSend(trimmed);
      setValue('');
    }
  };

  return (
    <div className="shrink-0 p-4 bg-white/80 dark:bg-slate-900/80 border-t border-slate-200 dark:border-slate-700 backdrop-blur-sm">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
        <div className="flex gap-2 items-end rounded-2xl bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-600 shadow-inner focus-within:ring-2 focus-within:ring-indigo-500/50 focus-within:border-indigo-400 dark:focus-within:border-indigo-500 transition-shadow">
          <input
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Message PC Builder..."
            className="flex-1 bg-transparent px-4 py-3 text-slate-900 dark:text-slate-100 placeholder-slate-500 dark:placeholder-slate-400 text-[15px] focus:outline-none rounded-2xl"
            disabled={disabled}
          />
          <button
            type="submit"
            disabled={disabled || !value.trim()}
            className="shrink-0 m-1.5 w-10 h-10 rounded-xl bg-indigo-500 text-white flex items-center justify-center hover:bg-indigo-600 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-indigo-500 transition-colors"
            aria-label="Send"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}
