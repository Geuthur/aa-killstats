// Third Party
import { AlertTriangle, Crosshair, Skull, TrendingUp, Users } from 'lucide-react';
import { useTranslation } from 'react-i18next';

// AA Killstats
import type { CombatSummaryResponse } from '@/Api/schema';
import { FetchingLoader } from '@/Components/Loader';
import { formatNumber } from '@/Utils/eveOnline';

import styles from '@/Components/Killboard/KillboardStats.module.css';

interface KillboardStatsProps {
    data?: CombatSummaryResponse;
    isLoading: boolean;
}

export default function KillboardStats({ data, isLoading }: KillboardStatsProps) {
    const { t } = useTranslation();

    if (isLoading) {
        return (
            <div className="aa-loader-container">
                <FetchingLoader message={t('Loading statistics...')} />
            </div>
        );
    }

    if (!data) return null;

    const efficiency =
        data.destroyed_isk + data.lost_isk > 0
            ? (data.destroyed_isk / (data.destroyed_isk + data.lost_isk)) * 100
            : 0;

    const stats = [
        {
            title: t('Total Kills'),
            value: formatNumber(data.total_kills, ""),
            icon: Crosshair,
            color: '#60a5fa',
        },
        {
            title: t('Active PvP Pilots'),
            value: formatNumber(data.active_pvpers, ""),
            icon: Users,
            color: '#c084fc',
        },
        {
            title: t('ISK Destroyed'),
            value: formatNumber(data.destroyed_isk),
            icon: TrendingUp,
            color: '#34d399',
        },
        {
            title: t('ISK Lost'),
            value: formatNumber(data.lost_isk),
            icon: AlertTriangle,
            color: '#fb7185',
        },
        {
            title: t('Efficiency'),
            value: `${efficiency.toFixed(1)}%`,
            icon: Skull,
            color: efficiency > 50 ? '#34d399' : '#fb7185',
        },
    ];

    return (
        <div className={`${styles['ks-stats-grid']}`}>
            {stats.map((stat, idx) => {
                const Icon = stat.icon;
                return (
                    <div
                        key={idx}
                        className={styles['ks-stat-card']}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                            <span className={styles['ks-stat-label']}>{stat.title}</span>
                            <Icon className={styles['ks-stat-icon']} color={stat.color} />
                        </div>
                        <span className={styles['ks-stat-value']}>{stat.value}</span>
                    </div>
                );
            })}
        </div>
    );
}
