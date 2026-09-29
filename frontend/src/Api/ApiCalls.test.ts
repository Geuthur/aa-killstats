// Third Party
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { apiClient } from '@/Api/Api';
import {
    fetchCombatStats,
    fetchCombatSummary,
    fetchHallStats,
    fetchKillmails,
    fetchTopAttackers,
    fetchTopVictims,
    loadAlliancesOverview,
    loadCorporationsOverview,
    loadMenu,
    loadUserData,
} from '@/Api/ApiCalls';
import { ProjectName } from '@/App';

describe('General API client functions', () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    describe('loadUserData', () => {
        it('returns user data on successful GET', async () => {
            const mockUser = { user_id: 1, character_id: 42, character_name: 'Test Pilot' };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockUser,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await loadUserData();
            expect(result).toEqual({ user: mockUser });
            expect(apiClient.GET).toHaveBeenCalledWith(`/${ProjectName}/api/user/`);
        });

        it('throws error when GET fails or returns no data', async () => {
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: undefined,
                error: { status: 500 },
                response: new Response(),
            } as never);

            await expect(loadUserData()).rejects.toThrow('Failed to load user data');
        });
    });

    describe('loadMenu', () => {
        it('calls /menu/ and returns data', async () => {
            const mockMenu = { left_links: [], right_links: [] };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockMenu,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await loadMenu();
            expect(result).toEqual(mockMenu);
            expect(apiClient.GET).toHaveBeenCalledWith(`/${ProjectName}/api/menu/`);
        });

        it('throws error when GET fails or returns no data', async () => {
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: undefined,
                error: { status: 500 },
                response: new Response(),
            } as never);

            await expect(loadMenu()).rejects.toThrow('Failed to load menu');
        });
    });

    describe('loadCorporationsOverview', () => {
        it('returns sorted corporations array on success', async () => {
            // Test Data
            const mockResponse = [
                {
                    corporation: {
                        '2': { corporation_id: 2, corporation_name: 'Beta Corp' },
                        '1': { corporation_id: 1, corporation_name: 'Alpha Corp' },
                    },
                },
            ];
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockResponse,
                error: undefined,
                response: new Response(),
            } as never);

            // Test Action
            const result = await loadCorporationsOverview();

            // Expected Result
            expect(result).toEqual([
                { id: 1, name: 'Alpha Corp' },
                { id: 2, name: 'Beta Corp' },
            ]);
            expect(apiClient.GET).toHaveBeenCalledWith(`/${ProjectName}/api/killboard/corporation/admin/`);
        });

        it('throws error when GET fails', async () => {
            // Test Data
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: undefined,
                error: { status: 500 },
                response: new Response(),
            } as never);

            // Test Action & Expected Result
            await expect(loadCorporationsOverview()).rejects.toThrow('Failed to load corporation overview');
        });
    });

    describe('loadAlliancesOverview', () => {
        it('returns sorted alliances array on success', async () => {
            // Test Data
            const mockResponse = [
                {
                    alliance: {
                        '10': { alliance_id: 10, alliance_name: 'Zenith Alliance' },
                        '9': { alliance_id: 9, alliance_name: 'Apex Alliance' },
                    },
                },
            ];
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockResponse,
                error: undefined,
                response: new Response(),
            } as never);

            // Test Action
            const result = await loadAlliancesOverview();

            // Expected Result
            expect(result).toEqual([
                { id: 9, name: 'Apex Alliance' },
                { id: 10, name: 'Zenith Alliance' },
            ]);
            expect(apiClient.GET).toHaveBeenCalledWith(`/${ProjectName}/api/killboard/alliance/admin/`);
        });

        it('throws error when GET fails', async () => {
            // Test Data
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: undefined,
                error: { status: 500 },
                response: new Response(),
            } as never);

            // Test Action & Expected Result
            await expect(loadAlliancesOverview()).rejects.toThrow('Failed to load alliance overview');
        });
    });

    describe('fetchCombatStats', () => {
        it('calls endpoint and returns data', async () => {
            const mockData = { total_kills: 5, active_pvpers: 2, destroyed_isk: 1000, lost_isk: 500, top_attackers: [], top_victims: [] };
            vi.spyOn(apiClient, 'GET').mockResolvedValueOnce({
                data: mockData,
                error: undefined,
                response: new Response(),
            } as never);

            const result = await fetchCombatStats(2026, 9, 'corporation', 123);
            expect(result).toEqual(mockData);
            expect(apiClient.GET).toHaveBeenCalledWith(
                '/killstats/api/stats/v2/year/{year}/month/{month}/{entity_type}/{entity_id}/',
                expect.objectContaining({
                    params: {
                        path: { year: 2026, month: 9, entity_type: 'corporation', entity_id: 123 },
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

            await expect(fetchCombatStats(2026, 9, 'corporation', 123)).rejects.toThrow('Failed to fetch combat stats');
        });
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
                '/killstats/api/stats/v2/summary/year/{year}/month/{month}/{entity_type}/{entity_id}/',
                expect.objectContaining({
                    params: {
                        path: { year: 0, month: 0, entity_type: 'alliance', entity_id: 456 },
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
                '/killstats/api/stats/v2/attackers/year/{year}/month/{month}/{entity_type}/{entity_id}/',
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
                '/killstats/api/stats/v2/victims/year/{year}/month/{month}/{entity_type}/{entity_id}/',
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
                '/killstats/api/hall/v2/year/{year}/month/{month}/{entity_type}/{entity_id}/',
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
                '/killstats/api/killmails/v2/year/{year}/month/{month}/{entity_type}/{entity_id}/',
                expect.objectContaining({
                    params: {
                        path: { year: 2026, month: 9, entity_type: 'corporation', entity_id: 123 },
                        query: { mode: 'losses', page: 2, page_size: 50 },
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
