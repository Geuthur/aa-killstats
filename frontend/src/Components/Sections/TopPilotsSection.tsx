// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Killstats
import { fetchTopAttackers, fetchTopVictims } from '@/Api/ApiCalls';
import { queryKeys } from '@/Api/query';
import type { TopPilotSchema } from '@/Api/schema';
import { FetchingLoader } from '@/Components/Loader';
import BaseModal, { ModalSize, type ModalData, useModalQueryState } from '@/Components/Modals/BaseModal';
import { formatNumber } from '@/Utils/eveOnline';

import styles from '@/Components/Sections/TopPilotSection.module.css';

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
        <div className={`${styles['ks-inner-panel']} ${styles['ks-inner-card']}`}>
            <h3 className={styles['ks-pilot-panel-title']}>{title}</h3>
            <div className={styles['ks-inner-default-div']}>
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
    pilots?: TopPilotSchema[];
    title: string;
    isVictims: boolean;
    isLoading: boolean;
}) {
    const { t } = useTranslation();

    if (isLoading) return <PilotCard title={title} />;

    if (!pilots?.length) {
        return (
            <div className={styles['ks-inner-panel']}>
                <h3 className={styles['ks-pilot-panel-title']}>{title}</h3>
                <p style={{ color: '#a1a1aa', fontSize: '.875rem' }}>{t('No data available.')}</p>
            </div>
        );
    }

    return (
        <div className={styles['ks-inner-panel']}>
            <h3 className={styles['ks-pilot-panel-title']}>{title}</h3>
            <div className={styles['ks-inner-div']}>
                {pilots.map((pilot, idx) => (
                    <div key={pilot.character_id} className={styles['ks-pilot-row']}>
                        <div className={styles['ks-pilot-rank']}>{idx + 1}</div>
                        <a
                            className="aa-cursor-pointer"
                            href={`https://zkillboard.com/character/${pilot.character_id}/`}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            <img
                                src={`https://images.evetech.net/characters/${pilot.character_id}/portrait?size=64`}
                                alt={pilot.character_name}
                                className={styles['ks-pilot-avatar']}
                            />
                        </a>
                        <div style={{ flex: 1, minWidth: 0 }}>
                            <div className="ks-external">
                                <a
                                    href={`https://zkillboard.com/character/${pilot.character_id}/`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className={styles['ks-pilot-name']}
                                >
                                    {pilot.character_name}
                                </a>
                            </div>
                            {pilot.main_name && (
                                <div className="ks-external">
                                    {t('Main: {{name}}', { name: pilot.main_name })}
                                </div>
                            )}
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            <div style={{ fontSize: '.75rem', fontWeight: 700, color: isVictims ? '#fb7185' : '#34d399' }}>
                                {isVictims
                                    ? t('{{count}} Losses', { count: pilot.count })
                                    : t('{{count}} Kills', { count: pilot.count })}
                            </div>
                            <div style={{ fontSize: '.75rem', color: '#a1a1aa', fontFamily: 'monospace' }}>
                                {t('{{amount}}', { amount: formatNumber(pilot.total_value) })}
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
        <div className={styles['ks-top-pilots-layout']}>
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
        >
            {content}
        </BaseModal>
    );
}

export { TopPilotsSection as TopPilotsModal };
export default TopPilotsSection;
