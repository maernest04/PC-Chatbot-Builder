import type { Build } from '../api/client';

type Props = {
  build: Build;
};

export function BuildCard({ build }: Props) {
  const formatPrice = (n: number) => `$${n.toFixed(2)}`;

  const handleExport = () => {
    const lines = [
      'PC Build',
      '--------',
      ...build.parts.map((p) => `${p.category}: ${p.name} - ${formatPrice(p.price_usd)}`),
      '',
      `Subtotal: ${formatPrice(build.subtotal)}`,
      `Tax (${(build.tax_rate * 100).toFixed(2)}%): ${formatPrice(build.subtotal * build.tax_rate)}`,
      `Total: ${formatPrice(build.total)}`,
    ];
    const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'pc-build.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800/90 shadow-lg overflow-hidden">
      <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-600 flex justify-between items-center bg-slate-50/50 dark:bg-slate-800/50">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-indigo-500/10 dark:bg-indigo-400/10 flex items-center justify-center">
            <svg className="w-5 h-5 text-indigo-500 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5.25 14.25h13.5m-13.5 0a3 3 0 01-3-3m3 3a3 3 0 100 6h13.5a3 3 0 100-6m-16.5-3a3 3 0 013-3h13.5a3 3 0 013 3m-19.5 0a4.5 4.5 0 01.9-2.7L5.737 5.1a3.375 3.375 0 012.7-1.35h7.126c1.062 0 2.062.5 2.7 1.35l2.587 3.45a4.5 4.5 0 01.9 2.7m0 0a3 3 0 01-3 3m0 3h.008v.008h-.008V18zm0-4.5h.008v.008h-.008V13.5z" />
            </svg>
          </div>
          <h3 className="font-semibold text-slate-800 dark:text-slate-100">Build summary</h3>
        </div>
        <button
          onClick={handleExport}
          className="text-sm font-medium text-indigo-500 hover:text-indigo-600 dark:text-indigo-400 dark:hover:text-indigo-300 flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-indigo-500/10 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-100/80 dark:bg-slate-700/50 text-left">
              <th className="px-4 py-3 font-medium text-slate-600 dark:text-slate-400 rounded-tl-lg">Category</th>
              <th className="px-4 py-3 font-medium text-slate-600 dark:text-slate-400">Part</th>
              <th className="px-4 py-3 font-medium text-slate-600 dark:text-slate-400 text-right rounded-tr-lg">Price</th>
            </tr>
          </thead>
          <tbody>
            {build.parts.map((p, i) => (
              <tr
                key={p.id}
                className={`border-t border-slate-100 dark:border-slate-600/80 hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors ${
                  i % 2 === 0 ? 'bg-white dark:bg-transparent' : 'bg-slate-50/50 dark:bg-slate-800/30'
                }`}
              >
                <td className="px-4 py-2.5 text-slate-600 dark:text-slate-400 font-medium">{p.category}</td>
                <td className="px-4 py-2.5 text-slate-800 dark:text-slate-100">
                  {p.link ? (
                    <a href={p.link} target="_blank" rel="noopener noreferrer" className="text-indigo-500 hover:text-indigo-600 dark:text-indigo-400 dark:hover:text-indigo-300 hover:underline">
                      {p.name}
                    </a>
                  ) : (
                    p.name
                  )}
                </td>
                <td className="px-4 py-2.5 text-right font-medium text-slate-800 dark:text-slate-100">{formatPrice(p.price_usd)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-5 py-4 border-t border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-800/50 flex flex-wrap items-center justify-end gap-4 text-sm">
        <span className="text-slate-500 dark:text-slate-400">Subtotal {formatPrice(build.subtotal)}</span>
        <span className="text-slate-500 dark:text-slate-400">Tax {(build.tax_rate * 100).toFixed(1)}%</span>
        <span className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-500 text-white font-semibold">
          Total {formatPrice(build.total)}
        </span>
      </div>
    </div>
  );
}
