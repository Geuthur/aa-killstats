// Third Party
import type { ColumnDef } from '@tanstack/react-table';
import { ExternalLink } from 'lucide-react';

// AA Killstats
import type { KillmailItem } from '@/Api/types';
import { renderTooltip } from '@/Utils';
import { formatNumber, getSecColor, formatRelativeTime } from '@/Utils/eveOnline';

export function getKillboardTableColumns(
  t: (key: string) => string,
): ColumnDef<KillmailItem>[] {
  return [
    {
      id: 'type',
      header: t('Type'),
      cell: ({ row }) => {
        const isLoss = Boolean(row.original.is_loss);
        return (
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider ${
              isLoss
                ? 'bg-rose-500/20 text-rose-300 border-killstats border-rose-500/40 shadow-sm'
                : 'bg-emerald-500/20 text-emerald-300 border-killstats border-emerald-500/40 shadow-sm'
            }`}
          >
            {isLoss ? t('LOSS') : t('KILL')}
          </span>
        );
      },
    },
    {
      header: t('Ship'),
      accessorKey: 'victim_ship_id',
      cell: ({ row }) => {
        const shipId = row.original.victim_ship_id;
        const shipName = row.original.victim_ship_name;
        const zkbLink =
          row.original.zkb_link ||
          `https://zkillboard.com/kill/${row.original.killmail_id}/`;
        return (
          <div className="flex items-center justify-center">
            {renderTooltip(
              `${shipName} - ${t('View Killmail')}`,
              <a
                href={zkbLink}
                target="_blank"
                rel="noopener noreferrer"
                className="block cursor-pointer"
              >
                <img
                  src={`https://images.evetech.net/types/${shipId}/render?size=128`}
                  alt={shipName}
                  className="w-12 h-12 sm:w-14 sm:h-14 rounded-lg object-contain bg-zinc-950/8 border-killstats hover:border-zinc-500 shadow-sm transition-transform hover:scale-125"
                  loading="lazy"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = `https://images.evetech.net/types/${shipId}/icon?size=64`;
                  }}
                />
              </a>,
            )}
          </div>
        );
      },
    },
    {
      header: t('Time'),
      accessorKey: 'killmail_date',
      cell: ({ getValue }) => {
        const dateStr = getValue<string>();
        return (
          <div className="flex flex-col">
            <span className="text-gray-300">
              {dateStr.substring(0, 16).replace('T', ' ')}
            </span>
            <span className="text-xs text-gray-500">{formatRelativeTime(dateStr)}</span>
          </div>
        );
      },
    },
    {
      header: t('Victim'),
      accessorKey: 'victim_name',
      cell: ({ row }) => {
        const victim = row.original.victim_name;
        const ship = row.original.victim_ship_name;
        const zkbLink =
          row.original.zkb_link ||
          `https://zkillboard.com/kill/${row.original.killmail_id}/`;
        return (
          <div className="flex flex-col">
            <span className="text-red-400 font-medium">{victim}</span>
            {renderTooltip(
              `${ship} - ${t('View Killmail')}`,
              <a
                href={zkbLink}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-gray-400 hover:text-gray-200 hover:underline transition-colors w-fit"
              >
                {ship}
              </a>,
            )}
          </div>
        );
      },
    },
    {
      header: t('Final Blow'),
      accessorKey: 'final_blow_name',
      cell: ({ getValue }) => {
        return (
          <span className="text-green-400 font-medium">
            {getValue<string>()}
          </span>
        );
      },
    },
    {
      header: t('Location'),
      accessorKey: 'solar_system_name',
      cell: ({ row }) => {
        const sys = row.original.solar_system_name;
        const sec = row.original.security_status;
        return (
          <div className="flex items-center gap-2">
            <span>{sys}</span>
            <span className={`font-bold sec-badge ${getSecColor(sec)}`}>
              {sec.toFixed(1)}
            </span>
          </div>
        );
      },
    },
    {
      header: t('Pilots'),
      accessorKey: 'pilot_count',
    },
    {
      header: t('ISK'),
      accessorKey: 'total_value',
      cell: ({ getValue }) => {
        return (
          <span className="font-medium text-gray-200">
            {formatNumber(getValue<number>())}
          </span>
        );
      },
    },
    {
      id: 'link',
      header: t('zKB'),
      cell: ({ row }) => {
        const zkbLink =
          row.original.zkb_link ||
          `https://zkillboard.com/kill/${row.original.killmail_id}/`;
        return renderTooltip(
          t('View on zKillboard'),
          <a
            href={zkbLink}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300 transition-colors text-xs font-bold uppercase inline-flex items-center gap-1"
          >
            <span>{t('View')}</span>
            <ExternalLink className="w-3 h-3" />
          </a>,
        );
      },
    },
  ];
}

export const columns: ColumnDef<KillmailItem>[] = getKillboardTableColumns(
  (key) => key,
);
