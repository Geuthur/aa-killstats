// React
import { MemoryRouter } from 'react-router-dom';

// Third Party
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NuqsTestingAdapter } from 'nuqs/adapters/testing';
import { describe, expect, it, vi } from 'vitest';

// AA Killstats
import { fetchKillmails } from '@/Api/ApiCalls';
import KillboardSection from '@/Components/Sections/KillboardSection';

vi.mock('@/Api/ApiCalls', () => {
    const pending = () => new Promise(() => undefined);
    return {
        fetchKillmails: vi.fn(),
        fetchCombatSummary: pending,
        fetchHallStats: pending,
        fetchTopAttackers: pending,
        fetchTopVictims: pending,
    };
});

const makePage = (name: string) => ({
    total: 120,
    killmails: [{
        killmail_id: 1,
        killmail_date: '2026-01-02T03:04:05Z',
        victim_id: 1,
        victim_name: name,
        victim_ship_id: 587,
        victim_ship_name: 'Rifter',
        final_blow_id: 2,
        final_blow_name: 'Hunter',
        solar_system_name: 'Jita',
        security_status: 0.9,
        pilot_count: 3,
        total_value: 1000000,
        is_loss: false,
        zkb_link: 'https://zkillboard.com/kill/1/',
    }],
});

describe('KillboardSection', () => {
    it('keeps the rows of the old page dimmed until the next page arrives', async () => {
        const user = userEvent.setup();
        let resolveNextPage: (value: unknown) => void = () => undefined;
        vi.mocked(fetchKillmails)
            .mockResolvedValueOnce(makePage('Old Page Victim') as never)
            .mockReturnValueOnce(new Promise((resolve) => { resolveNextPage = resolve; }) as never);

        const { container } = render(
            <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
                <NuqsTestingAdapter>
                    <MemoryRouter>
                        <KillboardSection entityType="alliance" entityId={1} />
                    </MemoryRouter>
                </NuqsTestingAdapter>
            </QueryClientProvider>,
        );
        await screen.findByText('Old Page Victim');

        await user.click(screen.getByRole('button', { name: 'Next Page' }));

        await waitFor(() => expect(container.querySelector('.aa-table-loading')).not.toBeNull());
        expect(screen.getByText('Old Page Victim')).toBeDefined();

        resolveNextPage(makePage('New Page Victim'));

        await screen.findByText('New Page Victim');
        expect(screen.queryByText('Old Page Victim')).toBeNull();
        expect(container.querySelector('.aa-table-loading')).toBeNull();
    });
});
