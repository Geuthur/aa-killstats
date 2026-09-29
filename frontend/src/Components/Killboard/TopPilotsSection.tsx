// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Killstats
import { fetchTopAttackers, fetchTopVictims } from '@/Api/ApiCalls';
import { queryKeys } from '@/Api/query';
import type { TopPilot } from '@/Api/types';
import { FetchingLoader } from '@/Components/Loader';
import BaseModal, { ModalSize, type ModalData, useModalQueryState } from '@/Components/Modals/BaseModal';
import { formatNumber } from '@/Utils/eveOnline';

export interface TopPilotsSectionProps {
    year: number | 'all';
    month: number | 'all';
    entityType: string;
    entityId: number;
    modalId?: string;
    show?: boolean;
    onHide?: () => void;
    asModal?: boolean;
}

function PilotCard({ title }: { title: string }) {
    const { t } = useTranslation();
    return (
        <div className="flex-1 rounded-xl border-killstats bg-[#0b0e14] p-5 flex flex-col min-h-[320px] shadow-sm backdrop-blur-md">
            <h3 className="text-base font-bold mb-4 text-white uppercase tracking-wider">{title}</h3>
            <div className="flex-1 flex items-center justify-center">
                <FetchingLoader message={t('Loading pilots...')} />
            </div>
        </div>
    );
}

function PilotList({
    pilots,
    title,
    isVictims,
    isLoading,
}: {
    pilots?: TopPilot[];
    title: string;
    isVictims: boolean;
    isLoading: boolean;
}) {
    const { t } = useTranslation();

    if (isLoading) return <PilotCard title={title} />;

    if (!pilots?.length) {
        return (
            <div className="flex-1 rounded-xl border-killstats bg-[#0b0e14] p-5 shadow-sm backdrop-blur-md">
                <h3 className="text-base font-bold mb-4 text-white uppercase tracking-wider">{title}</h3>
                <p className="text-zinc-400 text-sm">{t('No data available.')}</p>
            </div>
        );
    }

    return (
        <div className="flex-1 rounded-xl border-killstats bg-[#0b0e14] p-5 shadow-sm backdrop-blur-md">
            <h3 className="text-base font-bold mb-4 text-white uppercase tracking-wider">{title}</h3>
            <div className="space-y-2">
                {pilots.map((pilot, idx) => (
                    <div
                        key={pilot.character_id}
                        className="flex items-center gap-3 p-2.5 bg-zinc-700/60 m-1 rounded-lg border-killstats border-transparent hover:border-zinc-700/60 hover:bg-zinc-800/60 transition-all"
                    >
                        <div className="text-zinc-500 font-mono font-bold w-6 text-center text-sm">{idx + 1}</div>
                        <a
                            href={`https://zkillboard.com/character/${pilot.character_id}/`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="shrink-0 block cursor-pointer"
                        >
                            <img
                                src={`https://images.evetech.net/characters/${pilot.character_id}/portrait?size=64`}
                                alt={pilot.character_name}
                                className="w-10 h-10 rounded-lg border-killstats object-cover bg-zinc-900 hover:border-zinc-500 transition-colors"
                            />
                        </a>
                        <div className="flex-1 min-w-0">
                            <div className="text-sm font-semibold text-white truncate">
                                <a
                                    href={`https://zkillboard.com/character/${pilot.character_id}/`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="hover:underline hover:text-emerald-300 transition-colors block truncate"
                                >
                                    {pilot.character_name}
                                </a>
                            </div>
                            {pilot.main_name && (
                                <div className="text-xs text-zinc-400 truncate">
                                    {t('Main: {{name}}', { name: pilot.main_name })}
                                </div>
                            )}
                        </div>
                        <div className="text-right">
                            <div className={`text-xs sm:text-sm font-bold ${isVictims ? 'text-rose-400' : 'text-emerald-400'}`}>
                                {isVictims
                                    ? t('{{count}} Losses', { count: pilot.count })
                                    : t('{{count}} Kills', { count: pilot.count })}
                            </div>
                            <div className="text-xs text-zinc-400 font-mono">
                                {t('{{amount}} ISK', { amount: formatNumber(pilot.total_value) })}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export function TopPilotsSection({
    year,
    month,
    entityType,
    entityId,
    modalId = 'top-pilots',
    show,
    onHide,
    asModal = true,
}: TopPilotsSectionProps) {
    const { t } = useTranslation();
    const { activeModal, closeModal } = useModalQueryState();

    const isModalOpen = show !== undefined ? show : activeModal === modalId;
    const handleClose = onHide ?? closeModal;

    const shouldFetch = asModal ? isModalOpen : true;

    const { data: attackersData, isLoading: isLoadingAttackers } = useQuery({
        queryKey: queryKeys.TopAttackers(year, month, entityType, entityId),
        queryFn: () => fetchTopAttackers(year, month, entityType, entityId),
        enabled: shouldFetch,
    });

    const { data: victimsData, isLoading: isLoadingVictims } = useQuery({
        queryKey: queryKeys.TopVictims(year, month, entityType, entityId),
        queryFn: () => fetchTopVictims(year, month, entityType, entityId),
        enabled: shouldFetch,
    });

    const content = (
        <div className="flex flex-col md:flex-row gap-4">
            <PilotList
                pilots={attackersData?.pilots}
                title={t('Top 10 Attackers')}
                isVictims={false}
                isLoading={isLoadingAttackers}
            />
            <PilotList
                pilots={victimsData?.pilots}
                title={t('Top 10 Victims')}
                isVictims={true}
                isLoading={isLoadingVictims}
            />
        </div>
    );

    if (!asModal) {
        return content;
    }

    const modalData: ModalData = {
        title: t('Top 10 Pilots'),
        modal_id: modalId,
        text: '',
        icon: 'Trophy',
        url: '',
    };

    return (
        <BaseModal
            data={modalData}
            showModal={isModalOpen}
            setShowModal={(show) => {
                if (!show) handleClose();
            }}
            size={ModalSize.extraLarge}
            contentClassName="bg-zinc-900 text-zinc-100 border-killstats rounded-xl shadow-2xl"
        >
            {content}
        </BaseModal>
    );
}

export { TopPilotsSection as TopPilotsModal };
export default TopPilotsSection;

