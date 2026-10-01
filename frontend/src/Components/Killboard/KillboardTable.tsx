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

// Styles
import styles from '@/Components/Killboard/KillboardTable.module.css';

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
            <div className="aa-loader-container">
                <FetchingLoader message={t('Loading killmails...')} />
            </div>
        );
    }

    return (
        <div className={styles['ks-table-wrapper']}>
            <div
                style={{
                    overflowX: 'auto',
                    transition: 'opacity 200ms',
                    opacity: isLoading ? 0.6 : 1,
                    pointerEvents: isLoading ? 'none' : undefined,
                }}
            >
                <table className={styles['ks-table']}>
                    <thead className={styles['ks-table-header']}>
                        {table.getHeaderGroups().map((headerGroup) => (
                            <tr key={headerGroup.id}>
                                {headerGroup.headers.map((header) => (
                                    <th key={header.id} className={styles['ks-table-header-cell']}>
                                        {header.isPlaceholder
                                            ? null
                                            : flexRender(header.column.columnDef.header, header.getContext())}
                                    </th>
                                ))}
                            </tr>
                        ))}
                    </thead>
                    <tbody className={styles['ks-table-body']}>
                        {table.getRowModel().rows.length > 0 ? (
                            table.getRowModel().rows.map((row) => {
                                const isLoss = Boolean(row.original.is_loss);
                                return (
                                    <tr key={row.id} className={isLoss ? styles['ks-table-row-loss'] : styles['ks-table-row-kill']}>
                                        {row.getVisibleCells().map((cell) => (
                                            <td key={cell.id} className={styles['ks-table-row']}>
                                                {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                            </td>
                                        ))}
                                    </tr>
                                );
                            })
                        ) : (
                            <tr>
                                <td colSpan={columns.length} className={styles['ks-table-row']}>
                                    {t('No killmails found.')}
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            <div className={styles['ks-table-footer']}>
                <div className={styles['ks-pagination']}>
                    {renderTooltip(
                        t('First page'),
                        <span>
                            <button
                                className={styles['ks-pagination-btn']}
                                onClick={() => onPageChange(1)}
                                disabled={page <= 1 || isLoading}
                                aria-label={t('First page')}
                            >
                                <ChevronsLeft size="16" />
                            </button>
                        </span>,
                    )}
                    {renderTooltip(
                        t('Previous page'),
                        <span>
                            <button
                                className={styles['ks-pagination-btn']}
                                onClick={() => onPageChange(page - 1)}
                                disabled={page <= 1 || isLoading}
                                aria-label={t('Previous page')}
                            >
                                <ChevronLeft size="16" />
                            </button>
                        </span>,
                    )}
                    <span className={styles['ks-pagination-info']}>
                        {t('Page {{current}} of {{total}}', {
                            current: page,
                            total: pageCount,
                        })}
                    </span>
                    {renderTooltip(
                        t('Next page'),
                        <span>
                            <button
                                className={styles['ks-pagination-btn']}
                                onClick={() => onPageChange(page + 1)}
                                disabled={page >= pageCount || isLoading}
                                aria-label={t('Next page')}
                            >
                                <ChevronRight size="16" />
                            </button>
                        </span>,
                    )}
                    {renderTooltip(
                        t('Last page'),
                        <span>
                            <button
                                className={styles['ks-pagination-btn']}
                                onClick={() => onPageChange(pageCount)}
                                disabled={page >= pageCount || isLoading}
                                aria-label={t('Last page')}
                            >
                                <ChevronsRight size="16" />
                            </button>
                        </span>,
                    )}
                </div>
                <div className={styles['ks-pagination']} >
                    <span className={styles['ks-pagination-info']}>
                        {t('Total: {{count}} killmails', { count: total.toLocaleString() })}
                    </span>
                    <select
                        value={pageSize}
                        onChange={(e) => onPageSizeChange(Number(e.target.value))}
                        disabled={isLoading}
                        className={styles['ks-table-select']}
                    >
                        {[10, 25, 50, 100, 250].map((size) => (
                            <option key={size} value={size}>
                                {t('Show {{count}}', { count: size })}
                            </option>
                        ))}
                    </select>
                </div>
            </div>
        </div>
    );
}
