// Third Party
import { beforeEach, describe, expect, it, vi } from 'vitest';

// AA Killstats
import { apiClient } from '@/Api/Api';
import {
    loadAlliancesOverview,
    loadCorporationsOverview,
    overviewQueryKeys,
} from '@/Api/calls/overview';
import { ProjectName } from '@/constants';

describe('overviewQueryKeys', () => {
    it('provides the entities key', () => {
        expect(overviewQueryKeys.entities('corporation')).toEqual(['overview', 'corporation']);
    });
});

describe('Overview API calls', () => {
    beforeEach(() => {
        vi.restoreAllMocks();
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
});

/** Every call of `Api/calls/overview.ts`: [name, call, fixed text]. */
const calls: [string, () => Promise<unknown>, string][] = [
    ['loadCorporationsOverview', () => loadCorporationsOverview(), 'Failed to load corporation overview'],
    ['loadAlliancesOverview', () => loadAlliancesOverview(), 'Failed to load alliance overview'],
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
