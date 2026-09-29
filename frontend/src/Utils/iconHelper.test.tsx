// Third Party
import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

// AA Example
import getIcon from '@/Utils/iconHelper';

describe('iconHelper', () => {
    it('should render icon for known icon names', () => {
        // Test Data
        const { container } = render(getIcon({ name: 'ShieldAlert', size: 5, className: 'custom-class' }));

        // Test Action
        const svg = container.querySelector('svg');

        // Expected Result
        expect(svg).toBeTruthy();
        expect(svg?.getAttribute('class')).toContain('h-5');
        expect(svg?.getAttribute('class')).toContain('w-5');
        expect(svg?.getAttribute('class')).toContain('custom-class');
    });

    it('should render fallback icon for unknown icon names', () => {
        // Test Data
        const { container } = render(getIcon({ name: 'UnknownNonExistentIcon' }));

        // Test Action
        const svg = container.querySelector('svg');

        // Expected Result
        expect(svg).toBeTruthy();
        expect(svg?.getAttribute('class')).toContain('text-purple-400');
    });

    it('should support default size and default class', () => {
        // Test Data
        const { container } = render(getIcon({ name: 'ExternalLink' }));

        // Test Action
        const svg = container.querySelector('svg');

        // Expected Result
        expect(svg).toBeTruthy();
        expect(svg?.getAttribute('class')).toContain('h-6');
        expect(svg?.getAttribute('class')).toContain('text-zinc-400');
    });
});
