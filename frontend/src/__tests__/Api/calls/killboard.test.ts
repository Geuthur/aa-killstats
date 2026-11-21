// Third Party
import { beforeEach, describe, expect, it, vi } from 'vitest';

// AA Killstats
import { apiClient } from '@/Api/Api';
import {
    fetchCombatSummary,
    fetchHallStats,
    fetchKillmails,
    fetchTopAttackers,
    fetchTopVictims,
    killboardQueryKeys,
} from '@/Api/calls/killboard';

describe('killboardQueryKeys', () => {
    it('provides the parameterized keys', () => {
        expect(killboardQueryKeys.combatSummary(2026, 9, 'corporation', 123)).toEqual([
            'combatSummary',
            2026,
            9,
            'corporation',
            123,
        ]);
        expect(killboardQueryKeys.topAttackers(2026, 9, 'corporation', 123)).toEqual([
            'topAttackers',
            2026,
            9,
            'corporation',
            123,
        ]);
        expect(killboardQueryKeys.topVictims(2026, 9, 'corporation', 123)).toEqual([
            'topVictims',
            2026,
            9,
            'corporation',
            123,
        ]);
        expect(killboardQueryKeys.hallStats(2026, 9, 'corporation', 123)).toEqual([
            'hallStats',
            2026,
            9,
            'corporation',
            123,
        ]);
        expect(killboardQueryKeys.killmails(2026, 9, 'corporation', 123, 'kills')).toEqual([
            'killmails',
            2026,
            9,
            'corporation',
            123,
            'kills',
            1,
            25,
        ]);
        expect(killboardQueryKeys.killmails(2026, 9, 'corporation', 123, 'kills', 3, 50)).toEqual([
            'killmails',
            2026,
            9,
            'corporation',
            123,
            'kills',
            3,
            50,
        ]);
    });
});

describe('Killboard API calls', () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    describe('fetchCombatSummary', () => {
        it('calls endpoint and returns summary data', async () => {
            const mockData = { total_kills: 10, active_pvpers: 4, destroyed_isk: 2000, lost_isk: 100 };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockData,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await fetchCombatSummary('all', 'all', 'alliance', 456);
            expect(result).toEqual(mockData);
            expect(apiClient.GET).toHaveBeenCalledWith(
                '/killstats/api/stats/v2/summary/{entity_type}/{entity_id}/',
                expect.objectContaining({
                    params: {
                        path: { entity_type: 'alliance', entity_id: 456 },
                        query: {},
                    },
                })
            );
        });

        it('throws error when GET fails', async () => {
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: undefined,
                error: { status: 500 },
                response: new Response(),
            } as never);

            await expect(fetchCombatSummary(2026, 9, 'alliance', 456)).rejects.toThrow('Failed to fetch combat summary');
        });
    });

    describe('fetchTopAttackers & fetchTopVictims', () => {
        it('fetchTopAttackers calls attackers endpoint', async () => {
            const mockData = { pilots: [] };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockData,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await fetchTopAttackers(2026, 9, 'corporation', 123);
            expect(result).toEqual(mockData);
            expect(apiClient.GET).toHaveBeenCalledWith(
                '/killstats/api/stats/v2/attackers/{entity_type}/{entity_id}/',
                expect.any(Object)
            );
        });

        it('fetchTopVictims calls victims endpoint', async () => {
            const mockData = { pilots: [] };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockData,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await fetchTopVictims(2026, 9, 'corporation', 123);
            expect(result).toEqual(mockData);
            expect(apiClient.GET).toHaveBeenCalledWith(
                '/killstats/api/stats/v2/victims/{entity_type}/{entity_id}/',
                expect.any(Object)
            );
        });
    });

    describe('fetchHallStats', () => {
        it('calls hall endpoint and returns data', async () => {
            const mockData = { hall_of_fame: [], hall_of_shame: [] };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockData,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await fetchHallStats(2026, 9, 'corporation', 123);
            expect(result).toEqual(mockData);
            expect(apiClient.GET).toHaveBeenCalledWith(
                '/killstats/api/hall/v2/{entity_type}/{entity_id}/',
                expect.any(Object)
            );
        });

        it('throws error when GET fails', async () => {
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: undefined,
                error: { status: 500 },
                response: new Response(),
            } as never);

            await expect(fetchHallStats(2026, 9, 'corporation', 123)).rejects.toThrow('Failed to fetch hall stats');
        });
    });

    describe('fetchKillmails', () => {
        it('calls killmails endpoint with mode query and pagination', async () => {
            const mockData = { killmails: [], total: 0, page: 2, page_size: 50 };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockData,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await fetchKillmails(2026, 9, 'corporation', 123, 'losses', 2, 50);
            expect(result).toEqual(mockData);
            expect(apiClient.GET).toHaveBeenCalledWith(
                '/killstats/api/killmails/{entity_type}/{entity_id}/',
                expect.objectContaining({
                    params: {
                        path: { entity_type: 'corporation', entity_id: 123 },
                        query: { year: 2026, month: 9, mode: 'losses', page: 2, page_size: 50 },
                    },
                })
            );
        });

        it('calls killmails endpoint with all-time without year and month in query', async () => {
            const mockData = { killmails: [], total: 0, page: 1, page_size: 25 };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockData,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await fetchKillmails('all', 'all', 'alliance', 456);
            expect(result).toEqual(mockData);
            expect(apiClient.GET).toHaveBeenCalledWith(
                '/killstats/api/killmails/{entity_type}/{entity_id}/',
                expect.objectContaining({
                    params: {
                        path: { entity_type: 'alliance', entity_id: 456 },
                        query: { mode: 'all', page: 1, page_size: 25 },
                    },
                })
            );
        });

        it('throws error when GET fails', async () => {
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: undefined,
                error: { status: 500 },
                response: new Response(),
            } as never);

            await expect(fetchKillmails(2026, 9, 'corporation', 123)).rejects.toThrow('Failed to fetch killmails');
        });
    });
});

/** Every call of `Api/calls/killboard.ts`: [name, call, fixed text]. */
const calls: [string, () => Promise<unknown>, string][] = [
    ['fetchCombatSummary', () => fetchCombatSummary(2026, 9, 'alliance', 456), 'Failed to fetch combat summary'],
    ['fetchTopAttackers', () => fetchTopAttackers(2026, 9, 'alliance', 456), 'Failed to fetch top attackers'],
    ['fetchTopVictims', () => fetchTopVictims(2026, 9, 'alliance', 456), 'Failed to fetch top victims'],
    ['fetchHallStats', () => fetchHallStats(2026, 9, 'corporation', 123), 'Failed to fetch hall stats'],
    ['fetchKillmails', () => fetchKillmails(2026, 9, 'corporation', 123), 'Failed to fetch killmails'],
];

describe('Error messages of the API calls', () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    describe.each(calls)('%s', (_name, call, fixedText) => {
        it('should throw the message of the API when the request fails', async () => {
            // Test Data
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: undefined,
                error: { error: 'Permission Denied' },
                response: new Response(),
            } as never);

            // Test Action & Expected Result
            await expect(call()).rejects.toThrow('Permission Denied');
        });

        it('should throw the fixed text when the API sent no message', async () => {
            // Test Data
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: undefined,
                error: {},
                response: new Response(),
            } as never);

            // Test Action & Expected Result
            await expect(call()).rejects.toThrow(fixedText);
        });
    });
});
