// Third Party
import type { ColumnDef } from '@tanstack/react-table';

// AA Killstats
import type { KillmailItemSchema } from '@/Api/schema';
import { renderTooltip } from '@/Utils';
import { formatNumber, getSecColor, formatRelativeTime, renderCharacterPortrait } from '@/Utils/eveOnline';

import styles from '@/Components/Killboard/KillboardTableColumns.module.css';
import { renderLink, renderShipImage } from '@/Utils/general';

export function getKillboardTableColumns(
    t: (key: string) => string,
): ColumnDef<KillmailItemSchema>[] {
    return [
        {
            id: 'type',
            header: t('Type'),
            cell: ({ row }) => {
                const isLoss = Boolean(row.original.is_loss);
                return (
                    <span className={isLoss ? styles['ks-badge-loss'] : styles['ks-badge-kill']}>
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
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {renderTooltip(
                            `${shipName} - ${t('View Killmail')}`,
                            renderLink({
                                url: zkbLink,
                                text: '',
                                children: (
                                    renderShipImage(shipId, shipName, 'ks-ship-thumb')
                                ),
                                external: true,
                            }),
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
                    <div className={styles['ks-row']}>
                        <span style={{ color: '#d1d5db' }}>
                            {dateStr.substring(0, 16).replace('T', ' ')}
                        </span>
                        <span style={{ fontSize: '.75rem', color: '#6b7280' }}>
                            {formatRelativeTime(dateStr)}
                        </span>
                    </div>
                );
            },
        },
        {
            header: t('Victim'),
            accessorKey: 'victim_name',
            cell: ({ row }) => {
                const victim = row.original.victim_name;
                return (
                    <div className={styles['ks-row-inline']}>
                        {renderCharacterPortrait(row.original.victim_id, 64)}
                        {renderLink({
                            url: `https://zkillboard.com/character/${row.original.victim_id}/`,
                            text: '',
                            children: (
                                <span style={{ color: '#f87171', fontWeight: 500 }}>{victim}</span>
                            ),
                            external: true,
                            className: styles['aa-link-victim'],
                        })}
                    </div>
                );
            },
        },
        {
            header: t('Final Blow'),
            accessorKey: 'final_blow_name',
            cell: ({ getValue, row }) => {
                return (
                    <div className={styles['ks-row-inline']}>
                        {renderCharacterPortrait(row.original.final_blow_id, 64)}
                        {renderLink({
                            url: `https://zkillboard.com/character/${row.original.final_blow_id}/`,
                            text: '',
                            children: (
                                <span style={{ color: '#4ade80', fontWeight: 500 }}>
                                    {getValue<string>()}
                                </span>
                            ),
                            external: true,
                            className: styles['aa-link-final'],
                        })}
                    </div>
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
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span>{sys}</span>
                        <span className={`aa-badge-xs ${getSecColor(sec)}`}>
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
                    <span style={{ fontWeight: 500, color: '#e4e4e7' }}>
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
                    renderLink({
                        url: zkbLink,
                        text: t('View'),
                        external: true,
                        className: 'ks-zkb-link'
                    }),
                );
            },
        },
    ];
}

export const columns: ColumnDef<KillmailItemSchema>[] = getKillboardTableColumns(
    (key) => key,
);
