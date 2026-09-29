// React
import { useMemo } from 'react';

// Third Party
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import { useTranslation } from 'react-i18next';

// AA Killstats
import type { KillmailItemSchema } from '@/Api/schema';
import { getKillboardTableColumns } from '@/Components/Killboard/KillboardTableColumns';
import { FetchingLoader } from '@/Components/Loader';
import { renderTooltip } from '@/Utils';

interface KillboardTableProps {
  data: KillmailItemSchema[];
  total: number;
  page: number;
  pageSize: number;
  onPageChange: (newPage: number) => void;
  onPageSizeChange: (newPageSize: number) => void;
  isLoading: boolean;
}

export default function KillboardTable({
  data,
  total,
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
  isLoading,
}: KillboardTableProps) {
  const { t } = useTranslation();
  const tableData = useMemo(() => data, [data]);
  const columns = useMemo(() => getKillboardTableColumns(t), [t]);
  const pageCount = Math.max(1, Math.ceil(total / pageSize));

  const table = useReactTable({
    data: tableData,
    columns,
    pageCount,
    state: {
      pagination: {
        pageIndex: page - 1,
        pageSize,
      },
    },
    manualPagination: true,
    getCoreRowModel: getCoreRowModel(),
  });

  if (isLoading && !data.length) {
    return (
      <div className="w-full min-h-[280px] bg-zinc-900/60 rounded-xl border-killstats flex flex-col items-center justify-center p-12 backdrop-blur-md">
        <FetchingLoader message={t('Loading killmails...')} />
      </div>
    );
  }

  return (
    <div className="rounded-xl shadow-lg overflow-hidden border-killstats bg-zinc-900/60 backdrop-blur-md">
      <div className={`overflow-x-auto transition-opacity duration-200 ${isLoading ? 'opacity-60 pointer-events-none' : 'opacity-100'}`}>
        <table className="w-full text-sm text-left text-zinc-300">
          <thead className="bg-[#0b0e14] border-b border-zinc-700/80 text-zinc-400 uppercase text-[11px] font-semibold tracking-wider">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th key={header.id} className="px-4 py-3 font-medium">
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-zinc-800/80">
            {table.getRowModel().rows.length > 0 ? (
              table.getRowModel().rows.map((row) => {
                const isLoss = Boolean(row.original.is_loss);
                return (
                  <tr
                    key={row.id}
                    className={`transition-colors ${
                      isLoss
                        ? 'border-rose-900/50 bg-rose-950/20 hover:bg-rose-950/35 border-l-4 border-l-rose-500'
                        : 'hover:bg-zinc-800/50 border-l-4 border-l-transparent hover:border-l-emerald-500/50'
                    }`}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td key={cell.id} className="px-4 py-2.5 whitespace-nowrap text-zinc-300 text-xs sm:text-sm">
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-zinc-500">
                  {t('No killmails found.')}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-between p-3.5 border-t border-zinc-700/80 text-xs text-zinc-400 gap-3 bg-[#0b0e14]/90">
        <div className="flex items-center gap-2">
          {renderTooltip(
            t('First page'),
            <span>
              <button
                className="p-1.5 rounded-lg border border-zinc-700 bg-zinc-800 text-zinc-300 hover:bg-zinc-700 hover:text-white disabled:opacity-40 cursor-pointer transition-colors"
                onClick={() => onPageChange(1)}
                disabled={page <= 1 || isLoading}
                aria-label={t('First page')}
              >
                <ChevronsLeft className="w-4 h-4" />
              </button>
            </span>,
          )}
          {renderTooltip(
            t('Previous page'),
            <span>
              <button
                className="p-1.5 rounded-lg border border-zinc-700 bg-zinc-800 text-zinc-300 hover:bg-zinc-700 hover:text-white disabled:opacity-40 cursor-pointer transition-colors"
                onClick={() => onPageChange(page - 1)}
                disabled={page <= 1 || isLoading}
                aria-label={t('Previous page')}
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
            </span>,
          )}
          <span className="text-xs sm:text-sm text-zinc-400 font-mono">
            {t('Page {{current}} of {{total}}', {
              current: page,
              total: pageCount,
            })}
          </span>
          {renderTooltip(
            t('Next page'),
            <span>
              <button
                className="p-1.5 rounded-lg border border-zinc-700 bg-zinc-800 text-zinc-300 hover:bg-zinc-700 hover:text-white disabled:opacity-40 cursor-pointer transition-colors"
                onClick={() => onPageChange(page + 1)}
                disabled={page >= pageCount || isLoading}
                aria-label={t('Next page')}
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </span>,
          )}
          {renderTooltip(
            t('Last page'),
            <span>
              <button
                className="p-1.5 rounded-lg border border-zinc-700 bg-zinc-800 text-zinc-300 hover:bg-zinc-700 hover:text-white disabled:opacity-40 cursor-pointer transition-colors"
                onClick={() => onPageChange(pageCount)}
                disabled={page >= pageCount || isLoading}
                aria-label={t('Last page')}
              >
                <ChevronsRight className="w-4 h-4" />
              </button>
            </span>,
          )}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-zinc-400">
            {t('Total: {{count}} killmails', { count: total.toLocaleString() })}
          </span>
          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            disabled={isLoading}
            className="bg-zinc-800 border border-zinc-700 text-zinc-200 rounded-lg px-2.5 py-1 text-xs focus:outline-none focus:border-blue-500 cursor-pointer transition-colors"
          >
            {[10, 25, 50, 100, 250].map((size) => (
              <option key={size} value={size} className="bg-zinc-800 text-zinc-200">
                {t('Show {{count}}', { count: size })}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
