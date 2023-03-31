/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ModuleWithProviders, NgModule } from '@angular/core';

import { StoreModule } from '@ngrx/store';
import { StoreRouterConnectingModule } from '@ngrx/router-store';
import { EffectsModule } from '@ngrx/effects';
import { StoreDevtoolsConfig, StoreDevtoolsModule } from '@ngrx/store-devtools';

import { RouterService, RouterServiceImpl } from '../../router';
import { SharedRouterSerializer } from '../../router/integration/ngrx';

import { ComponentService, ComponentServiceImpl } from '../../component';

import { SHARED_ROOT_REDUCERS } from '../reducers';
import { SHARED_ROOT_EFFECTS } from '../effects';
import { NGRX_STORE_CONFIG, NGRX_STORE_DEVTOOLS_CONFIG } from '../config';
import { STORE_ROUTER } from '../state';

/**
 * ** VDK NgRx Redux module recommended for use in Development builds.
 */
@NgModule({
    imports: [
        StoreModule.forRoot(SHARED_ROOT_REDUCERS, NGRX_STORE_CONFIG),
        EffectsModule.forRoot(SHARED_ROOT_EFFECTS),
        StoreDevtoolsModule.instrument(() => VdkSharedNgrxDevModule.storeDevToolsConfig),
        StoreRouterConnectingModule.forRoot({
            stateKey: STORE_ROUTER,
            serializer: SharedRouterSerializer
        })
    ],
    exports: [StoreModule, EffectsModule, StoreDevtoolsModule, StoreRouterConnectingModule]
})
export class VdkSharedNgrxDevModule {
    private static storeDevToolsConfig: StoreDevtoolsConfig = NGRX_STORE_DEVTOOLS_CONFIG;

    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment,@typescript-eslint/no-explicit-any
    static forRoot(config: StoreDevtoolsConfig = {} as any): ModuleWithProviders<VdkSharedNgrxDevModule> {
        VdkSharedNgrxDevModule.storeDevToolsConfig = {
            ...NGRX_STORE_DEVTOOLS_CONFIG,
            ...config
        };

        return {
            ngModule: VdkSharedNgrxDevModule,
            providers: [
                { provide: RouterService, useClass: RouterServiceImpl },
                { provide: ComponentService, useClass: ComponentServiceImpl }
            ]
        };
    }
}
