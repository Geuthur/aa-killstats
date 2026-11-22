// React
import { MemoryRouter } from 'react-router-dom';

// Third Party
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

// AA Killstats
import type { KillmailItemSchema } from '@/Api/schema';
import KillboardTable from '@/Components/Killboard/KillboardTable';

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
        isFetching: false,
        ...overrides,
    };
    const { container } = render(
        <MemoryRouter>
            <KillboardTable {...props} />
        </MemoryRouter>,
    );
    return { ...props, container };
};

describe('KillboardTable', () => {
    it('renders all columns and one row per killmail', () => {
        const { container } = renderTable();

        expect(container.querySelector('.aa-table-shell')).not.toBeNull();
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

        expect(screen.getAllByText('Page 2 of 5').length).toBeGreaterThan(0);

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
        renderTable({ page: 1, total: 60 });

        expect((screen.getByRole('button', { name: 'First Page' }) as HTMLButtonElement).disabled).toBe(true);
        expect((screen.getByRole('button', { name: 'Next Page' }) as HTMLButtonElement).disabled).toBe(false);
    });

    it('hides the paging buttons on a single page', () => {
        renderTable({ page: 1, total: 10 });

        expect(screen.queryByRole('button', { name: 'Next Page' })).toBeNull();
    });

    it('shows the total and offers the page size of 250 without show all', () => {
        renderTable({ total: 1234 });

        expect(screen.getByText(/Total: 1,?234 killmails/)).toBeDefined();
        expect(screen.getByRole('option', { name: '250' })).toBeDefined();
        expect(screen.queryByRole('option', { name: 'Show All' })).toBeNull();
    });

    it('marks loss rows, not kill rows', () => {
        const { container } = renderTable();

        const rows = container.querySelectorAll('.aa-table-body tr');
        expect(rows[0].className).not.toContain('ks-table-row-loss');
        expect(rows[1].className).toContain('ks-table-row-loss');
    });

    it('shows the loader on the first load', () => {
        renderTable({ data: [], total: 0, page: 1, isLoading: true });

        expect(screen.getByText('Loading killmails...')).toBeDefined();
        expect(screen.queryByText('No killmails found.')).toBeNull();
    });

    it('shows the refresh indicator while fetching', () => {
        const { container } = renderTable({ isFetching: true });

        expect(container.querySelector('.fa-sync')).not.toBeNull();
    });

    it('dims the rows and locks the controls while reloading', () => {
        const { container } = renderTable({ isLoading: true });

        expect(screen.getByText('Victim 10')).toBeDefined();
        expect(container.querySelector('.opacity-50')).not.toBeNull();
        expect((screen.getByRole('button', { name: 'Next Page' }) as HTMLButtonElement).disabled).toBe(true);
        expect((screen.getByRole('combobox') as HTMLSelectElement).disabled).toBe(true);
    });
});
