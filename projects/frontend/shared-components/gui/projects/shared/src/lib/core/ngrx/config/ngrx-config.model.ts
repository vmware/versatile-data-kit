/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { RootStoreConfig } from '@ngrx/store';
import { StoreDevtoolsConfig } from '@ngrx/store-devtools';

/**
 * ** Configuration for NgRx Store Devtools.
 */
export const NGRX_STORE_DEVTOOLS_CONFIG: StoreDevtoolsConfig = {
    maxAge: 100,
    serialize: true,
    logOnly: false,
    name: 'Taurus NgRx Store'
};

/**
 * ** Configuration for NgRx Store.
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
 */
export interface TaurusNgRxConfig {
    /**
     * ** StoreDevTools configuration replica.
     * <p>see {@link https://ngrx.io/guide/store-devtools/config}</p>
     */
    storeDevToolsConfig?: StoreDevtoolsConfig;
}
