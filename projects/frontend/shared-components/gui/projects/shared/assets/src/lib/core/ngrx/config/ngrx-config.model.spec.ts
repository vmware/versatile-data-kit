

import { NGRX_STORE_CONFIG, NGRX_STORE_DEVTOOLS_CONFIG } from './ngrx-config.model';

describe('NGRX_STORE_DEVTOOLS_CONFIG', () => {
    it('should verify default values are set', () => {
        // Then
        expect(NGRX_STORE_DEVTOOLS_CONFIG).toEqual({
            maxAge: 100,
            serialize: true,
            logOnly: false,
            name: 'Taurus NgRx Store'
        });
    });
});

describe('NGRX_STORE_CONFIG', () => {
    it('should verify default values are set', () => {
        // Then
        expect(NGRX_STORE_CONFIG).toEqual({
            runtimeChecks: {
                strictActionImmutability: true,
                strictStateImmutability: true
            }
        });
    });
});
