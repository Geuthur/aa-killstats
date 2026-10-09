// React
import { useState } from 'react';

// Third Party
import { Flame, ShieldAlert, Skull, Trophy } from 'lucide-react';
import { useTranslation } from 'react-i18next';

// Styles
import styles from '@/Components/Killboard/KillboardHallOfFame.module.css';

// AA Killstats
import type { HallEntrySchema, HallResponse } from '@/Api/schema';
import { FetchingLoader } from '@/Components/Loader';
import { renderTooltip } from '@/Utils';
import { formatNumber, zKillboardLink } from '@/Utils/eveOnline';

export interface KillboardHallOfFameProps {
    data?: HallResponse;
    isLoading: boolean;
    className?: string;
}

interface RankStyle {
    cardStyle: string;
    shipStyle: string;
    badgeStyle: string;
    glowStyle: string;
    label: string;
}

function getRankStyle(index: number, t: (key: string) => string): RankStyle {
    switch (index) {
        case 0:
            return {
                cardStyle: 'ks-pilot-card-1',
                shipStyle: 'ks-pilot-ship-1',
                badgeStyle: 'ks-pilot-badge-1',
                glowStyle: 'ks-pilot-glow-1',
                label: t('Gold'),
            };
        case 1:
            return {
                cardStyle: 'ks-pilot-card-2',
                shipStyle: 'ks-pilot-ship-2',
                badgeStyle: 'ks-pilot-badge-2',
                glowStyle: 'ks-pilot-glow-2',
                label: t('Silver'),
            };
        case 2:
            return {
                cardStyle: 'ks-pilot-card-3',
                shipStyle: 'ks-pilot-ship-3',
                badgeStyle: 'ks-pilot-badge-3',
                glowStyle: 'ks-pilot-glow-3',
                label: t('Bronze'),
            };
        default:
            return {
                cardStyle: 'ks-pilot-card-default',
                shipStyle: 'ks-pilot-ship-default',
                badgeStyle: 'ks-pilot-badge-default',
                glowStyle: 'ks-pilot-glow-default',
                label: '',
            };
    }
}

export default function KillboardHallOfFame({
    data,
    isLoading,
    className = '',
}: KillboardHallOfFameProps) {
    const { t } = useTranslation();
    const [activeTab, setActiveTab] = useState<'fame' | 'shame'>('fame');

    const entries: HallEntrySchema[] =
        (activeTab === 'fame' ? data?.hall_of_fame : data?.hall_of_shame) ?? [];

    return (
        <div className={`aa-panel-lg ${className} p-5`}>
            {/* Header with Tab Switcher */}
            <div className={styles['ks-section-header']}>
                <div>
                    <h3 className="ks-h3">
                        {activeTab === 'fame' ? (
                            <>
                                <Trophy size="20" color="#facc15" />
                                <span>{t('HALL OF FAME')}</span>
                            </>
                        ) : (
                            <>
                                <Skull size="20" color="#f43f5e" />
                                <span>{t('HALL OF SHAME')}</span>
                            </>
                        )}
                    </h3>
                    <p className="aa-section-subtitle mt-2">
                        {activeTab === 'fame'
                            ? t('Most valuable kills by our pilots in the selected period.')
                            : t('Highest losses by our pilots in the selected period.')}
                    </p>
                </div>

                <div className="aa-tab-bar">
                    <button
                        onClick={() => setActiveTab('fame')}
                        className={`ks-tab-btn${activeTab === 'fame' ? ' active ' + styles['ks-tab-btn-fame'] : ''}`}
                    >
                        <Flame size="14" />
                        <span>{t('Hall of Fame')}</span>
                    </button>

                    <button
                        onClick={() => setActiveTab('shame')}
                        className={`ks-tab-btn${activeTab === 'shame' ? ' active ' + styles['ks-tab-btn-shame'] : ''}`}
                    >
                        <ShieldAlert size="14" />
                        <span>{t('Hall of Shame')}</span>
                    </button>
                </div>
            </div>

            {/* Content */}
            {isLoading ? (
                <div className={styles['ks-hof-loading']}>
                    <FetchingLoader message={t('Loading hall of fame...')} />
                </div>
            ) : entries.length === 0 ? (
                <div className={styles['ks-hof-empty']}>
                    <div className={styles['ks-hof-empty-icon']}>
                        {activeTab === 'shame' ? (
                            <Skull size="24" color="#f43f5e" />
                        ) : (
                            <Trophy size="24" color="#facc15" />
                        )}
                    </div>
                    <div className="ks-text">
                        {t('No records found for this period.')}
                    </div>
                </div>
            ) : (
                <div className={styles['ks-hof-grid']}>
                    {entries.map((entry, index) => {
                        const isShame = activeTab === 'shame';
                        const shipId = isShame ? entry.victim_ship_id : (entry.victim_ship_id || entry.ship_id);
                        const shipName = isShame
                            ? entry.victim_ship_name
                            : (entry.victim_ship_name || entry.ship_name || t('Unknown Ship'));
                        const pilotShipName = !isShame && entry.ship_name ? entry.ship_name : null;
                        const rankStyle = getRankStyle(index, t);

                        return (
                            <div
                                key={`${entry.killmail_id}-${entry.char_id}-${index}`}
                                className={`${styles[rankStyle.cardStyle]} ${styles['group']} ${styles['ks-hof-card']}`}
                            >
                                {/* Full-bleed Character Portrait Background */}
                                {entry.char_id ? (
                                    <img
                                        src={`https://images.evetech.net/characters/${entry.char_id}/portrait?size=512`}
                                        alt={entry.char_name || 'Pilot'}
                                        className={styles['ks-hof-portrait']}
                                        loading="lazy"
                                    />
                                ) : (
                                    <div className={styles['ks-pilot-blend-default']}>
                                        <Skull style={{ width: '64px', height: '64px' }} />
                                    </div>
                                )}

                                {/* Cinematic Gradient Overlays */}
                                <div className={` ${styles['ks-pilot-glow']} ${styles[rankStyle.glowStyle]}`} />
                                <div className={styles['ks-hof-overlay-bottom']} />

                                {/* Top Section: Rank & ISK Value */}
                                <div className={styles['ks-pilot-top-content']}>
                                    <span className={` ${styles['ks-hof-rank']} ${styles[rankStyle.badgeStyle]}`}>
                                        <span>#{index + 1}</span>
                                        {rankStyle.label ? (
                                            <span className={styles['ks-pilot-rank-label']}>
                                                ({rankStyle.label})
                                            </span>
                                        ) : null}
                                    </span>

                                    <span className={isShame ? 'ks-isk-negative' : 'ks-isk-positive'}>
                                        {formatNumber(entry.total_value)}
                                    </span>
                                </div>

                                {/* Bottom Content */}
                                <div className={styles['ks-bottom-content']}>
                                    <div style={{ minWidth: 0, flex: 1 }}>
                                        {/* Bottom Content Pilot Info */}
                                        <div className={styles['ks-bottom-pilot']}>
                                            {entry.char_id ? (
                                                zKillboardLink({id: entry.char_id, name: entry.char_name, className: styles['ks-bottom-char-link']})
                                            ) : (
                                                entry.char_name || '—'
                                            )}
                                        </div>

                                        {/* Bottom Content Pilot Ship Info */}
                                        {pilotShipName && (
                                            <div className={styles['ks-bottom-ship-info']}>
                                                <span>{t('Ship:')}</span>{' '}
                                                <span className={styles['ks-bottom-ship-name']}>{pilotShipName}</span>
                                            </div>
                                        )}

                                        {/* Bottom Content Pilot Ship Icon */}
                                        <div className={styles['ks-bottom-ship-icon']}>
                                            <span>
                                                {isShame ? t('Lost:') : t('Target:')}
                                            </span>{' '}
                                            {entry.killmail_id ? (
                                                zKillboardLink({id: entry.killmail_id, name: shipName, className: styles['ks-bottom-ship-icon-link']})
                                            ) : (
                                                <span className={styles['ks-bottom-ship-name']}>{shipName}</span>
                                            )}
                                        </div>

                                        {/* Bottom Content Pilot Damage Done */}
                                        {!isShame && entry.damage_done ? (
                                            <div className={styles['ks-bottom-damage']}>
                                                {t('Damage: {{amount}}', { amount: formatNumber(entry.damage_done, '') })}
                                            </div>
                                        ) : null}

                                        {entry.killmail_id ? (
                                            zKillboardLink({id: entry.killmail_id, name: t('Killmail'), className: 'ks-zkb-link', externalLink: true})
                                        ) : null}
                                    </div>

                                    {/* Ship Portrait */}
                                    {shipId ? (
                                        <div style={{ flexShrink: 0 }}>
                                            {entry.killmail_id ? (
                                                renderTooltip(
                                                    `${shipName} - ${t('View Killmail')}`,
                                                    <a
                                                        className="aa-cursor-pointer"
                                                        href={entry.zkb_link || `https://zkillboard.com/kill/${entry.killmail_id}/`}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                    >
                                                        <img
                                                            src={`https://images.evetech.net/types/${shipId}/render?size=512`}
                                                            alt={shipName}
                                                            className={`${styles['ks-hof-ship']} ${styles[rankStyle.shipStyle]}`}
                                                            loading="lazy"
                                                            onError={(e) => {
                                                                (e.target as HTMLImageElement).src = `https://images.evetech.net/types/${shipId}/icon?size=64`;
                                                            }}
                                                        />
                                                    </a>,
                                                )
                                            ) : (
                                                renderTooltip(
                                                    shipName,
                                                    <div className="aa-cursor-pointer">
                                                        <img
                                                            src={`https://images.evetech.net/types/${shipId}/render?size=512`}
                                                            alt={shipName}
                                                            className={`${styles['ks-hof-ship']} ${styles[rankStyle.shipStyle]}`}
                                                            loading="lazy"
                                                            onError={(e) => {
                                                                (e.target as HTMLImageElement).src = `https://images.evetech.net/types/${shipId}/icon?size=64`;
                                                            }}
                                                        />
                                                    </div>,
                                                )
                                            )}
                                        </div>
                                    ) : null}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
