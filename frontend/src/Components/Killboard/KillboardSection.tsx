// React
import { useState } from 'react';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { Trophy, Users } from 'lucide-react';
import { createParser, useQueryState } from 'nuqs';
import { useTranslation } from 'react-i18next';

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
import TopPilotsSection from '@/Components/Killboard/TopPilotsSection';
import { useModalQueryState } from '@/Components/Modals';

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

    // --- Parallel queries: summary loads fast, top-lists load independently ---

    /** Counters & ISK – lightweight, appears first */
    const { data: summaryData, isLoading: isLoadingSummary } = useQuery({
        queryKey: queryKeys.CombatSummary(year, month, entityType, entityId),
        queryFn: () => fetchCombatSummary(year, month, entityType, entityId),
    });

    /** Hall of Fame / Shame */
    const { data: hallData, isLoading: isLoadingHall } = useQuery({
        queryKey: queryKeys.HallStats(year, month, entityType, entityId),
        queryFn: () => fetchHallStats(year, month, entityType, entityId),
    });

    /** Killmails list – filtered by mode and paginated */
    const { data: killmailsData, isLoading: isLoadingKillmails } = useQuery({
        queryKey: queryKeys.Killmails(year, month, entityType, entityId, killmailMode, page, pageSize),
        queryFn: () => fetchKillmails(year, month, entityType, entityId, killmailMode, page, pageSize),
        refetchInterval: 60_000, // refresh every 60 seconds
        refetchIntervalInBackground: false, // Do not refetch in the background
        retry: 1,
    });

    return (
        <div className="flex flex-col gap-6 text-gray-100 p-4">
            <KillboardFilterBar
                year={year}
                month={month}
                onYearChange={(newYear) => {
                    setYear(newYear);
                    setPage(1);
                }}
                onMonthChange={(newMonth) => {
                    setMonth(newMonth);
                    setPage(1);
                }}
            />

            {/* Stats bar: shows immediately when the fast summary arrives */}
            <KillboardStats data={summaryData} isLoading={isLoadingSummary} />

            {/* Banner with button to open Top 10 Modal */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-zinc-900/60 border-killstats rounded-xl p-4">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-lg bg-zinc-800/80 border-killstats text-amber-400">
                        <Trophy className="h-5 w-5" />
                    </div>
                    <div>
                        <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-0.5">
                            {t('Top 10 Rankings')}
                        </h4>
                        <p className="text-xs text-zinc-400 mb-0">
                            {t('View the most active attackers and highest loss pilots.')}
                        </p>
                    </div>
                </div>
                <button
                    className="flex items-center gap-2 px-3.5 py-1.5 self-start sm:self-auto bg-zinc-950/70 rounded-md text-xs border-killstats hover:border-zinc-500 font-bold tracking-wider transition-all cursor-pointer text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50 cursor-pointer"
                    onClick={() => openModal('top-pilots')}
                >
                    <Users className="w-4 h-4" />
                    <span>{t('Open Top 10 Pilots')}</span>
                </button>
            </div>

            {/* Hall of Fame in its own dedicated full-width container */}
            <KillboardHallOfFame data={hallData} isLoading={isLoadingHall} />

            {/* Killmail Log Table - on the same page with mode filter */}
            <div className="flex flex-col gap-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-zinc-900/60 border-killstats rounded-xl p-4">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2 m-0">
                        <span>{t('Killmails Log')}</span>
                        {killmailsData?.total !== undefined && (
                            <span className="text-xs font-mono px-2 py-0.5 rounded bg-zinc-800 border-killstats text-zinc-300">
                                {killmailsData.total}
                            </span>
                        )}
                    </h3>

                    {/* Mode Filter: All / Kills / Losses */}
                    <div className="flex items-center gap-1.5 p-1 bg-zinc-950/70 border-killstats rounded-lg self-start sm:self-auto">
                        <button
                            onClick={() => {
                                setKillmailMode('all');
                                setPage(1);
                            }}
                            className={`px-3 py-1 rounded-md text-xs font-bold transition-all cursor-pointer ${killmailMode === 'all'
                                    ? 'bg-blue-600 text-white shadow-sm'
                                    : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
                                }`}
                        >
                            {t('All')}
                        </button>
                        <button
                            onClick={() => {
                                setKillmailMode('kills');
                                setPage(1);
                            }}
                            className={`px-3 py-1 rounded-md text-xs font-bold transition-all cursor-pointer ${killmailMode === 'kills'
                                    ? 'bg-emerald-600 text-white shadow-sm'
                                    : 'text-zinc-400 hover:text-emerald-300 hover:bg-zinc-800/50'
                                }`}
                        >
                            {t('Kills')}
                        </button>
                        <button
                            onClick={() => {
                                setKillmailMode('losses');
                                setPage(1);
                            }}
                            className={`px-3 py-1 rounded-md text-xs font-bold transition-all cursor-pointer ${killmailMode === 'losses'
                                    ? 'bg-rose-600 text-white shadow-sm'
                                    : 'text-zinc-400 hover:text-rose-300 hover:bg-zinc-800/50'
                                }`}
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
                    onPageSizeChange={(newSize) => {
                        setPageSize(newSize);
                        setPage(1);
                    }}
                    isLoading={isLoadingKillmails}
                />
            </div>

            {/* Top 10 Pilots Modal dialog managed via modal system */}
            <TopPilotsSection
                year={year}
                month={month}
                entityType={entityType}
                entityId={entityId}
            />
        </div>
    );
}
