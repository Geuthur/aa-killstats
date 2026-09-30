// Third Party
import { Form } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

import styles from '@/Components/Killboard/KillboardFilterBar.module.css';

export interface KillboardFilterBarProps {
    year: number | 'all';
    month: number | 'all';
    onYearChange: (year: number | 'all') => void;
    onMonthChange: (month: number | 'all') => void;
}

export default function KillboardFilterBar({
    year,
    month,
    onYearChange,
    onMonthChange,
}: KillboardFilterBarProps) {
    const { t } = useTranslation();
    const currentYear = new Date().getFullYear();
    const years: (number | 'all')[] = [
        ...Array.from({ length: 6 }, (_, i) => currentYear - i),
        'all',
    ];

    const monthNames = [
        t('January'), t('February'), t('March'), t('April'),
        t('May'), t('June'), t('July'), t('August'),
        t('September'), t('October'), t('November'), t('December'),
    ];

    const months: (number | 'all')[] = [
        ...Array.from({ length: 12 }, (_, i) => i + 1),
        'all',
    ];

    return (
        <div className={`aa-panel p-4 ${styles['ks-panel-container']}`}>
            <h2 className={`ks-title ${styles['ks-title']}`}>{t('Killboard Statistics')}</h2>
            <div className={`${styles['ks-filter-container']}`}>
                <Form.Group className="d-flex align-items-center gap-2 m-0">
                    <Form.Label className={`ks-filter-label ${styles['ks-filter-label']}`}>
                        {t('Year')}:
                    </Form.Label>
                    <Form.Select
                        value={year}
                        onChange={(e) =>
                            onYearChange(
                                e.target.value === 'all' ? 'all' : parseInt(e.target.value, 10)
                            )
                        }
                        className={`${styles['ks-filter-select']}`}
                        style={{ width: 'auto', minWidth: '120px' }}
                    >
                        {years.map((y) => (
                            <option key={y} value={y}>
                                {y === 'all' ? t('All Time') : y}
                            </option>
                        ))}
                    </Form.Select>
                </Form.Group>

                <Form.Group className="d-flex align-items-center gap-2 m-0">
                    <Form.Label className={`ks-filter-label ${styles['ks-filter-label']}`}>
                        {t('Month')}:
                    </Form.Label>
                    <Form.Select
                        value={month}
                        onChange={(e) =>
                            onMonthChange(
                                e.target.value === 'all' ? 'all' : parseInt(e.target.value, 10)
                            )
                        }
                        className={`${styles['ks-filter-select']}`}
                        style={{ width: 'auto', minWidth: '160px' }}
                    >
                        {months.map((m) => (
                            <option key={m} value={m}>
                                {m === 'all'
                                    ? t('All Months')
                                    : `${m} - ${monthNames[(m as number) - 1]}`}
                            </option>
                        ))}
                    </Form.Select>
                </Form.Group>
            </div>
        </div>
    );
}
