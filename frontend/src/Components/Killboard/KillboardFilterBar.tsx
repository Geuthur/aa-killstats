// Third Party
import { Form } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

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
    t('January'),
    t('February'),
    t('March'),
    t('April'),
    t('May'),
    t('June'),
    t('July'),
    t('August'),
    t('September'),
    t('October'),
    t('November'),
    t('December'),
  ];

  const months: (number | 'all')[] = [
    ...Array.from({ length: 12 }, (_, i) => i + 1),
    'all',
  ];

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border-killstats bg-zinc-900/60 p-4 shadow-sm backdrop-blur-md">
      <h2 className="text-xl sm:text-2xl font-bold m-0 text-white tracking-wide">{t('Killboard Statistics')}</h2>
      <div className="flex flex-wrap items-center gap-3">
        <Form.Group className="d-flex align-items-center gap-2 m-0">
          <Form.Label className="m-0 text-xs sm:text-sm font-medium text-zinc-300">
            {t('Year')}:
          </Form.Label>
          <Form.Select
            value={year}
            onChange={(e) =>
              onYearChange(
                e.target.value === 'all' ? 'all' : parseInt(e.target.value, 10)
              )
            }
            className="bg-zinc-800 border-zinc-700 text-zinc-200 text-xs sm:text-sm rounded-lg py-1.5 px-3 hover:border-zinc-500 focus:border-blue-500 focus:outline-none transition-colors cursor-pointer"
            style={{ width: 'auto', minWidth: '120px' }}
          >
            {years.map((y) => (
              <option key={y} value={y} className="bg-zinc-800 text-zinc-200">
                {y === 'all' ? t('All Time') : y}
              </option>
            ))}
          </Form.Select>
        </Form.Group>

        <Form.Group className="d-flex align-items-center gap-2 m-0">
          <Form.Label className="m-0 text-xs sm:text-sm font-medium text-zinc-300">
            {t('Month')}:
          </Form.Label>
          <Form.Select
            value={month}
            onChange={(e) =>
              onMonthChange(
                e.target.value === 'all' ? 'all' : parseInt(e.target.value, 10)
              )
            }
            className="bg-zinc-800 border-zinc-700 text-zinc-200 text-xs sm:text-sm rounded-lg py-1.5 px-3 hover:border-zinc-500 focus:border-blue-500 focus:outline-none transition-colors cursor-pointer"
            style={{ width: 'auto', minWidth: '160px' }}
          >
            {months.map((m) => (
              <option key={m} value={m} className="bg-zinc-800 text-zinc-200">
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
