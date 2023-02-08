

import { RootStoreConfig } from '@ngrx/store';
import { StoreDevtoolsConfig } from '@ngrx/store-devtools';

/**
 * ** Configuration for NgRx Store Devtools.
 *
 * @author gorankokin
 */
export const NGRX_STORE_DEVTOOLS_CONFIG: StoreDevtoolsConfig = {
    maxAge: 100,
    serialize: true,
    logOnly: false,
    name: 'Taurus NgRx Store'
};


/**
 * ** Configuration for NgRx Store.
 *
 * @author gorankokin
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const NGRX_STORE_CONFIG: RootStoreConfig<any> = {
    runtimeChecks: {
        strictActionImmutability: true,
        strictStateImmutability: true
    }
};

/**
 * ** Config for Taurus impl of NgRx.
 *
 * @author gorankokin
 */
export interface TaurusNgRxConfig {
    /**
     * ** StoreDevTools configuration replica.
     * <p>see {@link https://ngrx.io/guide/store-devtools/config}</p>
     */
    storeDevToolsConfig?: StoreDevtoolsConfig;
}
