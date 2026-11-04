// React
import { useMemo } from 'react';

// Third Party
import { useTranslation } from 'react-i18next';

// Styles
import styles from '@/Components/Killboard/KillboardTable.module.css';

// AA Killstats
import type { KillmailItemSchema } from '@/Api/schema';
import BaseTable from '@/Components/Base/BaseTable/BaseTable';
import { getKillboardTableColumns } from '@/Components/Killboard/KillboardTableColumns';

interface KillboardTableProps {
    data: KillmailItemSchema[];
    total: number;
    page: number;
    pageSize: number;
    onPageChange: (newPage: number) => void;
    onPageSizeChange: (newPageSize: number) => void;
    isLoading: boolean;
    isFetching?: boolean;
}

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100, 250];

export default function KillboardTable({
    data,
    total,
    page,
    pageSize,
    onPageChange,
    onPageSizeChange,
    isLoading,
    isFetching = false,
}: KillboardTableProps) {
    const { t } = useTranslation();
    const columns = useMemo(() => getKillboardTableColumns(t), [t]);

    return (
        <BaseTable
            data={data}
            columns={columns}
            isLoading={isLoading}
            isFetching={isFetching}
            loadingText={t('Loading killmails...')}
            emptyText={t('No killmails found.')}
            pageSizeOptions={PAGE_SIZE_OPTIONS}
            serverPagination={{
                page,
                pageSize,
                total,
                onPageChange,
                onPageSizeChange,
                totalText: t('Total: {{total}} killmails', { total: total.toLocaleString() }),
            }}
            getRowClassName={(row) =>
                row.original.is_loss ? styles['ks-table-row-loss'] : styles['ks-table-row-kill']
            }
        />
    );
}
