// Third Party
import { AlertTriangle, Crosshair, Skull, TrendingUp, Users } from 'lucide-react';
import { useTranslation } from 'react-i18next';

// AA Killstats
import type { CombatSummaryResponse } from '@/Api/types';
import { FetchingLoader } from '@/Components/Loader';
import { formatNumber } from '@/Utils/eveOnline';

interface KillboardStatsProps {
  data?: CombatSummaryResponse;
  isLoading: boolean;
}

export default function KillboardStats({ data, isLoading }: KillboardStatsProps) {
  const { t } = useTranslation();

  if (isLoading) {
    return (
      <div className="w-full bg-zinc-900/60 rounded-xl border-killstats p-8 flex items-center justify-center shadow-sm min-h-[120px] backdrop-blur-md">
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
      color: 'text-blue-400',
    },
    {
      title: t('Active PvP Pilots'),
      value: formatNumber(data.active_pvpers, ""),
      icon: Users,
      color: 'text-purple-400',
    },
    {
      title: t('ISK Destroyed'),
      value: formatNumber(data.destroyed_isk),
      icon: TrendingUp,
      color: 'text-emerald-400',
    },
    {
      title: t('ISK Lost'),
      value: formatNumber(data.lost_isk),
      icon: AlertTriangle,
      color: 'text-rose-400',
    },
    {
      title: t('Efficiency'),
      value: `${efficiency.toFixed(1)}%`,
      icon: Skull,
      color: efficiency > 50 ? 'text-emerald-400' : 'text-rose-400',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <div
            key={idx}
            className="rounded-xl border-killstats bg-zinc-900/60 p-4 sm:p-5 shadow-sm flex flex-col justify-between backdrop-blur-md hover:border-zinc-600 transition-all"
          >
            <div className="flex justify-between items-start mb-2">
              <span className="text-zinc-400 text-xs sm:text-sm font-medium font-mono uppercase tracking-wider">{stat.title}</span>
              <Icon className={`w-4 h-4 sm:w-5 sm:h-5 ${stat.color}`} />
            </div>
            <span className="text-xl md:text-2xl font-bold text-white tracking-tight">{stat.value}</span>
          </div>
        );
      })}
    </div>
  );
}
