// React
import { MemoryRouter } from 'react-router-dom';

// Third Party
import { render, screen } from '@testing-library/react';
import { createInstance } from 'i18next';
import { I18nextProvider, initReactI18next } from 'react-i18next';
import { describe, expect, it, vi } from 'vitest';

// AA Killstats
import KillboardTable from '@/Components/Killboard/KillboardTable';

const i18n = createInstance();
i18n.use(initReactI18next).init({
    lng: 'de',
    keySeparator: false,
    nsSeparator: false,
    interpolation: { escapeValue: false },
    react: { useSuspense: false },
    resources: {
        de: { translation: { 'Total: {{total}} killmails': 'Insgesamt: {{total}} Killmails' } },
    },
});

describe('KillboardTable translation', () => {
    it('translates the total with real i18next', () => {
        render(
            <I18nextProvider i18n={i18n}>
                <MemoryRouter>
                    <KillboardTable
                        data={[]}
                        total={120}
                        page={1}
                        pageSize={25}
                        onPageChange={vi.fn()}
                        onPageSizeChange={vi.fn()}
                        isLoading={false}
                    />
                </MemoryRouter>
            </I18nextProvider>,
        );

        expect(screen.getByText('Insgesamt: 120 Killmails')).toBeDefined();
    });
});
