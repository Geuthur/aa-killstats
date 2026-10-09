// Third Party
import { describe, expect, it } from 'vitest';

import { queryKeys } from '@/Api/query';

describe('queryKeys', () => {
    it('provides static query keys', () => {
        expect(queryKeys.Menu).toEqual(['Menu']);
        expect(queryKeys.User).toEqual(['User']);
    });

    it('provides parameterized query keys', () => {
        expect(queryKeys.Overview('corporation')).toEqual(['overview', 'corporation']);
        expect(queryKeys.CombatSummary(2026, 9, 'corporation', 123)).toEqual([
            'combatSummary',
            2026,
            9,
            'corporation',
            123,
        ]);
        expect(queryKeys.TopAttackers(2026, 9, 'corporation', 123)).toEqual([
            'topAttackers',
            2026,
            9,
            'corporation',
            123,
        ]);
        expect(queryKeys.TopVictims(2026, 9, 'corporation', 123)).toEqual([
            'topVictims',
            2026,
            9,
            'corporation',
            123,
        ]);
        expect(queryKeys.HallStats(2026, 9, 'corporation', 123)).toEqual([
            'hallStats',
            2026,
            9,
            'corporation',
            123,
        ]);
        expect(queryKeys.Killmails(2026, 9, 'corporation', 123, 'kills')).toEqual([
            'killmails',
            2026,
            9,
            'corporation',
            123,
            'kills',
            1,
            25,
        ]);
        expect(queryKeys.Killmails(2026, 9, 'corporation', 123, 'kills', 3, 50)).toEqual([
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
