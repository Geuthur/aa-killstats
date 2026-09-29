// React
import { useState } from 'react';

// Third Party
import { ExternalLink, Flame, ShieldAlert, Skull, Trophy } from 'lucide-react';
import { useTranslation } from 'react-i18next';

// AA Killstats
import type { HallEntry, HallResponse } from '@/Api/types';
import { FetchingLoader } from '@/Components/Loader';
import { renderTooltip } from '@/Utils';
import { formatNumber } from '@/Utils/eveOnline';

export interface KillboardHallOfFameProps {
  data?: HallResponse;
  isLoading: boolean;
  className?: string;
}

interface RankStyle {
  cardBorder: string;
  shipBorder: string;
  badge: string;
  label: string;
  glow: string;
}

function getRankStyle(index: number, t: (key: string) => string): RankStyle {
  switch (index) {
    case 0:
      return {
        cardBorder:
          'border-killstats shadow-[0_0_20px_rgba(250,204,21,0.2)] hover:border-yellow-400',
        shipBorder:
          'border-2 border-yellow-400 shadow-[0_0_16px_rgba(250,204,21,0.7)] hover:border-yellow-300 ring-1 ring-yellow-400/50',
        badge:
          'bg-gradient-to-r from-yellow-400 to-amber-500 text-black font-extrabold border border-yellow-300 shadow-[0_0_12px_rgba(250,204,21,0.6)]',
        label: t('Gold'),
        glow: 'from-yellow-500/15',
      };
    case 1:
      return {
        cardBorder:
          'border-killstats shadow-[0_0_20px_rgba(203,213,225,0.15)] hover:border-slate-300',
        shipBorder:
          'border-2 border-slate-300 shadow-[0_0_16px_rgba(203,213,225,0.6)] hover:border-slate-200 ring-1 ring-slate-300/50',
        badge:
          'bg-gradient-to-r from-slate-200 to-slate-400 text-black font-extrabold border border-slate-200 shadow-[0_0_12px_rgba(203,213,225,0.5)]',
        label: t('Silver'),
        glow: 'from-slate-400/15',
      };
    case 2:
      return {
        cardBorder:
          'border-killstats shadow-[0_0_20px_rgba(180,83,9,0.15)] hover:border-amber-600',
        shipBorder:
          'border-2 border-amber-600 shadow-[0_0_16px_rgba(180,83,9,0.6)] hover:border-amber-500 ring-1 ring-amber-600/50',
        badge:
          'bg-gradient-to-r from-amber-600 to-amber-800 text-amber-100 font-extrabold border border-amber-500 shadow-[0_0_12px_rgba(180,83,9,0.5)]',
        label: t('Bronze'),
        glow: 'from-amber-700/15',
      };
    default:
      return {
        cardBorder:
          'border-killstats hover:border-zinc-500 shadow-sm hover:shadow-md',
        shipBorder: 'border-killstats shadow-md hover:border-zinc-500',
        badge: 'bg-zinc-800/90 text-zinc-300 border border-zinc-700',
        label: '',
        glow: 'from-zinc-800/10',
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

  const entries: HallEntry[] =
    (activeTab === 'fame' ? data?.hall_of_fame : data?.hall_of_shame) ?? [];

  return (
    <div
      className={`rounded-xl border-killstats bg-zinc-900/60 p-5 sm:p-6 shadow-sm ${className}`}
    >
      {/* Header with Tab Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-700/80 pb-4 mb-6">
        <div>
          <h3 className="text-lg sm:text-xl font-bold tracking-tight text-white flex items-center gap-2">
            {activeTab === 'fame' ? (
              <>
                <Trophy className="h-5 w-5 text-amber-400" />
                <span>{t('HALL OF FAME')}</span>
              </>
            ) : (
              <>
                <Skull className="h-5 w-5 text-rose-400" />
                <span>{t('HALL OF SHAME')}</span>
              </>
            )}
          </h3>
          <p className="mt-0.5 text-xs text-zinc-400">
            {activeTab === 'fame'
              ? t('Most valuable kills by our pilots in the selected period.')
              : t('Highest losses by our pilots in the selected period.')}
          </p>
        </div>

        {/* Tab Switcher: Hall of Fame vs Hall of Shame */}
        <div className="flex items-center gap-2 p-1 bg-zinc-950/70 border-killstats rounded-lg self-start sm:self-auto">
          <button
            onClick={() => setActiveTab('fame')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-md text-xs font-bold uppercase tracking-wider transition-all cursor-pointer ${
              activeTab === 'fame'
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
            }`}
          >
            <Flame className="h-3.5 w-3.5" />
            <span>{t('Hall of Fame')}</span>
          </button>

          <button
            onClick={() => setActiveTab('shame')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-md text-xs font-bold uppercase tracking-wider transition-all cursor-pointer ${
              activeTab === 'shame'
                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
            }`}
          >
            <ShieldAlert className="h-3.5 w-3.5" />
            <span>{t('Hall of Shame')}</span>
          </button>
        </div>
      </div>

      {/* Content Cards */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24 bg-zinc-950/40 rounded-2xl border-killstats">
          <FetchingLoader message={t('Loading hall of fame...')} />
        </div>
      ) : entries.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="p-3 rounded-full bg-zinc-800/50 border border-zinc-700/50 mb-3 text-zinc-500">
            {activeTab === 'shame' ? (
              <Skull className="h-6 w-6" />
            ) : (
              <Trophy className="h-6 w-6" />
            )}
          </div>
          <div className="text-sm font-semibold text-zinc-300">
            {t('No records found for this period.')}
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
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
                className={`group relative rounded-2xl overflow-hidden h-[360px] sm:h-[400px] flex flex-col justify-between p-4.5 transition-all duration-500 ${rankStyle.cardBorder} bg-zinc-950 shadow-md hover:shadow-2xl`}
              >
                {/* Full-bleed Character Portrait Background with Zoom Effect on Hover */}
                {entry.char_id ? (
                  <img
                    src={`https://images.evetech.net/characters/${entry.char_id}/portrait?size=512`}
                    alt={entry.char_name || 'Pilot'}
                    className="absolute inset-0 w-full h-full object-cover object-center transition-transform duration-700 ease-out group-hover:scale-110"
                    loading="lazy"
                  />
                ) : (
                  <div className="absolute inset-0 w-full h-full flex items-center justify-center bg-zinc-900 text-zinc-700">
                    <Skull className="h-16 w-16" />
                  </div>
                )}

                {/* Cinematic Gradient Overlays */}
                <div
                  className={`absolute inset-0 bg-gradient-to-b ${rankStyle.glow} via-black/30 to-black/95 pointer-events-none`}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/95 via-black/45 to-transparent pointer-events-none" />

                {/* Top Section: Rank & ISK Value */}
                <div className="relative z-10 flex flex-col items-start gap-1.5">
                  <span
                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-mono ${rankStyle.badge}`}
                  >
                    <span>#{index + 1}</span>
                    {rankStyle.label ? (
                      <span className="hidden sm:inline text-[10px] tracking-wide uppercase font-bold">
                        ({rankStyle.label})
                      </span>
                    ) : null}
                  </span>

                  <span
                    className={`text-xs sm:text-sm font-bold px-2.5 py-1 rounded-md backdrop-blur-md shadow-sm ${
                      isShame
                        ? 'bg-rose-950/80 text-rose-300 border border-rose-500/50'
                        : 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/50'
                    }`}
                  >
                    {formatNumber(entry.total_value)}
                  </span>
                </div>

                {/* Bottom Content: Character details + Ship + Killmail Link */}
                <div className="relative z-10 flex items-end justify-between gap-3 pt-4">
                  <div className="min-w-0 flex-1">
                    <div className="text-base sm:text-lg font-bold text-white truncate drop-shadow-md hover:text-emerald-300 transition-colors">
                      {entry.char_id ? (
                        renderTooltip(
                          entry.char_name || '',
                          <a
                            href={`https://zkillboard.com/character/${entry.char_id}/`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:underline text-white block truncate"
                          >
                            {entry.char_name || '—'}
                          </a>,
                        )
                      ) : (
                        entry.char_name || '—'
                      )}
                    </div>

                    {pilotShipName && (
                      <div className="text-[11px] text-zinc-400 truncate drop-shadow-sm">
                        <span>{t('Flown:')}</span>{' '}
                        <span className="font-semibold text-zinc-200">{pilotShipName}</span>
                      </div>
                    )}

                    <div className="text-xs text-zinc-300 truncate drop-shadow-sm mt-0.5">
                      <span className="text-zinc-400">
                        {isShame ? t('Lost:') : t('Target:')}
                      </span>{' '}
                      {entry.killmail_id ? (
                        renderTooltip(
                          `${shipName} - ${t('View Killmail')}`,
                          <a
                            href={entry.zkb_link || `https://zkillboard.com/kill/${entry.killmail_id}/`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-semibold text-zinc-100 hover:text-amber-300 hover:underline transition-colors"
                          >
                            {shipName}
                          </a>,
                        )
                      ) : (
                        <span className="font-semibold text-zinc-100">{shipName}</span>
                      )}
                    </div>

                    {!isShame && entry.damage_done ? (
                      <div className="text-[11px] font-mono text-amber-300 drop-shadow-sm mt-0.5">
                        {t('Damage: {{amount}}', { amount: formatNumber(entry.damage_done, "") })}
                      </div>
                    ) : null}

                    {entry.killmail_id ? (
                      renderTooltip(
                        t('View Killmail on zKillboard'),
                        <a
                          href={entry.zkb_link || `https://zkillboard.com/kill/${entry.killmail_id}/`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-900/90 hover:bg-zinc-800 text-zinc-200 hover:text-white text-xs font-mono transition-all border border-zinc-700/80 backdrop-blur-md shadow-sm"
                        >
                          <span>{t('Killmail')}</span>
                          <ExternalLink className="h-3 w-3" />
                        </a>,
                      )
                    ) : null}
                  </div>

                  {/* Ship Portrait */}
                  {shipId ? (
                    <div className="shrink-0">
                      {entry.killmail_id ? (
                        renderTooltip(
                          `${shipName} - ${t('View Killmail')}`,
                          <a
                            href={entry.zkb_link || `https://zkillboard.com/kill/${entry.killmail_id}/`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block cursor-pointer"
                          >
                            <img
                              src={`https://images.evetech.net/types/${shipId}/render?size=512`}
                              alt={shipName}
                              className={`w-16 h-16 sm:w-20 sm:h-20 object-contain drop-shadow-md rounded-xl bg-zinc-950/90 backdrop-blur-md transition-transform duration-300 hover:scale-125 ${rankStyle.shipBorder}`}
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
                          <div className="block cursor-pointer">
                            <img
                              src={`https://images.evetech.net/types/${shipId}/render?size=512`}
                              alt={shipName}
                              className={`w-16 h-16 sm:w-20 sm:h-20 object-contain drop-shadow-md rounded-xl bg-zinc-950/90 backdrop-blur-md transition-transform duration-300 hover:scale-125 cursor-pointer ${rankStyle.shipBorder}`}
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
