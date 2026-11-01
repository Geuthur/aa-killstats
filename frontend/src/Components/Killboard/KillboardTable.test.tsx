// Third Party
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

// AA Killstats
import type { KillmailItemSchema } from '@/Api/schema';
import KillboardTable from '@/Components/Killboard/KillboardTable';

vi.mock('react-i18next', async (importOriginal) => ({
    ...(await importOriginal<typeof import('react-i18next')>()),
    useTranslation: () => ({
        t: (key: string, options?: Record<string, unknown>) =>
            options
                ? Object.entries(options).reduce(
                    (text, [name, value]) => text.replace(`{{${name}}}`, String(value)),
                    key,
                )
                : key,
    }),
}));

const makeKill = (id: number, isLoss: boolean): KillmailItemSchema => ({
    killmail_id: id,
    killmail_date: '2026-01-02T03:04:05Z',
    victim_id: 1,
    victim_name: `Victim ${id}`,
    victim_ship_id: 587,
    victim_ship_name: 'Rifter',
    final_blow_id: 2,
    final_blow_name: `Hunter ${id}`,
    solar_system_name: 'Jita',
    security_status: 0.9,
    pilot_count: 3,
    total_value: 1000000,
    is_loss: isLoss,
    zkb_link: `https://zkillboard.com/kill/${id}/`,
} as unknown as KillmailItemSchema);

const renderTable = (overrides: Partial<React.ComponentProps<typeof KillboardTable>> = {}) => {
    const props = {
        data: [makeKill(10, false), makeKill(11, true)],
        total: 120,
        page: 2,
        pageSize: 25,
        onPageChange: vi.fn(),
        onPageSizeChange: vi.fn(),
        isLoading: false,
        ...overrides,
    };
    render(<KillboardTable {...props} />);
    return props;
};

describe('KillboardTable', () => {
    it('renders all columns and one row per killmail', () => {
        renderTable();

        for (const header of ['Type', 'Ship', 'Time', 'Victim', 'Final Blow', 'Location', 'Pilots', 'ISK', 'zKB']) {
            expect(screen.getByRole('columnheader', { name: header })).toBeDefined();
        }
        expect(screen.getByText('KILL')).toBeDefined();
        expect(screen.getByText('LOSS')).toBeDefined();
        expect(screen.getByText('Victim 10')).toBeDefined();
        expect(screen.getByText('Hunter 11')).toBeDefined();
    });

    it('shows the empty message without data', () => {
        renderTable({ data: [], total: 0, page: 1 });

        expect(screen.getByText('No killmails found.')).toBeDefined();
    });

    it('shows the server-side page count and calls the page handlers', async () => {
        const user = userEvent.setup();
        const props = renderTable();

        expect(screen.getByText('Page 2 of 5')).toBeDefined();

        await user.click(screen.getByRole('button', { name: 'Next Page' }));
        expect(props.onPageChange).toHaveBeenCalledWith(3);

        await user.click(screen.getByRole('button', { name: 'Previous Page' }));
        expect(props.onPageChange).toHaveBeenCalledWith(1);

        await user.click(screen.getByRole('button', { name: 'Last Page' }));
        expect(props.onPageChange).toHaveBeenCalledWith(5);

        await user.selectOptions(screen.getByRole('combobox'), '50');
        expect(props.onPageSizeChange).toHaveBeenCalledWith(50);
    });

    it('disables paging at the boundaries', () => {
        renderTable({ page: 1, total: 10 });

        expect((screen.getByRole('button', { name: 'First Page' }) as HTMLButtonElement).disabled).toBe(true);
        expect((screen.getByRole('button', { name: 'Next Page' }) as HTMLButtonElement).disabled).toBe(true);
    });
});
