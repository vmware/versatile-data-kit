

import { RouterEffects } from '../../router/state/effects';

import { SHARED_ROOT_EFFECTS } from './root-effects.registry';

describe('SHARED_ROOT_EFFECTS', () => {
    it('should verify expected Effects are in this registry', () => {
        // Then
        expect(SHARED_ROOT_EFFECTS).toEqual([RouterEffects]);
    });
});
