// React
import { useState } from 'react';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { Trophy, Users } from 'lucide-react';
import { createParser, useQueryState } from 'nuqs';
import { useTranslation } from 'react-i18next';

// Styles
import styles from '@/Components/Sections/KillboardSection.module.css';

// AA Killstats
import {
    fetchCombatSummary,
    fetchHallStats,
    fetchKillmails,
} from '@/Api/ApiCalls';
import { queryKeys } from '@/Api/query';
import KillboardFilterBar from '@/Components/Killboard/KillboardFilterBar';
import KillboardHallOfFame from '@/Components/Killboard/KillboardHallOfFame';
import KillboardStats from '@/Components/Killboard/KillboardStats';
import KillboardTable from '@/Components/Killboard/KillboardTable';
import { useModalQueryState } from '@/Components/Modals';
import TopPilotsSection from '@/Components/Sections/TopPilotsSection';

export interface KillboardSectionProps {
    entityType: string;
    entityId: number;
}

const currentYear = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;

const parseYear = createParser<number | 'all'>({
    parse(v) {
        if (v === 'all') return 'all';
        const n = parseInt(v, 10);
        return isNaN(n) ? null : n;
    },
    serialize: String,
}).withDefault(currentYear);

const parseMonth = createParser<number | 'all'>({
    parse(v) {
        if (v === 'all') return 'all';
        const n = parseInt(v, 10);
        return isNaN(n) || n < 1 || n > 12 ? null : n;
    },
    serialize: String,
}).withDefault(currentMonth);

export default function KillboardSection({ entityType, entityId }: KillboardSectionProps) {
    const { t } = useTranslation();

    const [year, setYear] = useQueryState('year', parseYear);
    const [month, setMonth] = useQueryState('month', parseMonth);
    const [killmailMode, setKillmailMode] = useState<'all' | 'kills' | 'losses'>('all');
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(25);
    const { openModal } = useModalQueryState();

    const { data: summaryData, isLoading: isLoadingSummary } = useQuery({
        queryKey: queryKeys.CombatSummary(year, month, entityType, entityId),
        queryFn: () => fetchCombatSummary(year, month, entityType, entityId),
    });

    const { data: hallData, isLoading: isLoadingHall } = useQuery({
        queryKey: queryKeys.HallStats(year, month, entityType, entityId),
        queryFn: () => fetchHallStats(year, month, entityType, entityId),
    });

    const { data: killmailsData, isLoading: isLoadingKillmails } = useQuery({
        queryKey: queryKeys.Killmails(year, month, entityType, entityId, killmailMode, page, pageSize),
        queryFn: () => fetchKillmails(year, month, entityType, entityId, killmailMode, page, pageSize),
        refetchInterval: 60_000,
        refetchIntervalInBackground: false,
        retry: 1,
    });

    return (
        <div className={styles['killboard-section']}>
            <KillboardFilterBar
                year={year}
                month={month}
                onYearChange={(newYear) => { setYear(newYear); setPage(1); }}
                onMonthChange={(newMonth) => { setMonth(newMonth); setPage(1); }}
            />

            <KillboardStats data={summaryData} isLoading={isLoadingSummary} />

            {/* Banner with button to open Top 10 Modal */}
            <div className="aa-panel-lg ks-banner">
                <div className="ks-banner-inner">
                    <div className="ks-icon-badge" style={{ color: '#fbbf24' }}>
                        <Trophy size="20" />
                    </div>
                    <div>
                        <h4 className="ks-banner-title">
                            {t('Top 10 Rankings')}
                        </h4>
                        <p className="ks-banner-subtitle">
                            {t('View the most active attackers and highest loss pilots.')}
                        </p>
                    </div>
                </div>
                <button
                    className="ks-banner-btn"
                    onClick={() => openModal('top-pilots')}
                >
                    <Users size="16" />
                    <span>{t('Open Top 10 Pilots')}</span>
                </button>
            </div>

            <KillboardHallOfFame data={hallData} isLoading={isLoadingHall} />

            {/* Killmail Log Table */}
            <div className={styles['killmail-log-container']}>
                <div className="aa-panel-lg ks-log-header">
                    <h3 className="ks-log-title">
                        <span>{t('Killmails Log')}</span>
                        {killmailsData?.total !== undefined && (
                            <span className="ks-count-badge">
                                {killmailsData.total}
                            </span>
                        )}
                    </h3>

                    {/* Mode Filter */}
                    <div className="aa-tab-bar" style={{ alignSelf: 'flex-start' }}>
                        <button
                            onClick={() => { setKillmailMode('all'); setPage(1); }}
                            className={`ks-tab-btn${killmailMode === 'all' ? ' active ks-tab-btn-all' : ''}`}
                            style={{ padding: '4px 12px' }}
                        >
                            {t('All')}
                        </button>
                        <button
                            onClick={() => { setKillmailMode('kills'); setPage(1); }}
                            className={`ks-tab-btn${killmailMode === 'kills' ? ' active ks-tab-btn-kills' : ''}`}
                            style={{ padding: '4px 12px' }}
                        >
                            {t('Kills')}
                        </button>
                        <button
                            onClick={() => { setKillmailMode('losses'); setPage(1); }}
                            className={`ks-tab-btn${killmailMode === 'losses' ? ' active ks-tab-btn-losses' : ''}`}
                            style={{ padding: '4px 12px' }}
                        >
                            {t('Losses')}
                        </button>
                    </div>
                </div>

                <KillboardTable
                    data={killmailsData?.killmails ?? []}
                    total={killmailsData?.total ?? 0}
                    page={page}
                    pageSize={pageSize}
                    onPageChange={setPage}
                    onPageSizeChange={(newSize) => { setPageSize(newSize); setPage(1); }}
                    isLoading={isLoadingKillmails}
                />
            </div>

            <TopPilotsSection
                year={year}
                month={month}
                entityType={entityType}
                entityId={entityId}
            />
        </div>
    );
}
