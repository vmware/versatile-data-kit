/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ModuleWithProviders, NgModule } from '@angular/core';

import { StoreModule } from '@ngrx/store';
import { StoreRouterConnectingModule } from '@ngrx/router-store';
import { EffectsModule } from '@ngrx/effects';

import { RouterService, RouterServiceImpl } from '../../router';
import { SharedRouterSerializer } from '../../router/integration/ngrx';

import { ComponentService, ComponentServiceImpl } from '../../component';

import { SHARED_ROOT_REDUCERS } from '../reducers';
import { SHARED_ROOT_EFFECTS } from '../effects';
import { NGRX_STORE_CONFIG } from '../config';
import { STORE_ROUTER } from '../state';

/**
 * ** VDK NgRx Redux module recommended for use in Production builds.
 */
@NgModule({
    imports: [
        StoreModule.forRoot(SHARED_ROOT_REDUCERS, NGRX_STORE_CONFIG),
        EffectsModule.forRoot(SHARED_ROOT_EFFECTS),
        StoreRouterConnectingModule.forRoot({
            stateKey: STORE_ROUTER,
            serializer: SharedRouterSerializer
        })
    ],
    exports: [StoreModule, EffectsModule, StoreRouterConnectingModule]
})
export class VdkSharedNgrxProdModule {
    static forRoot(): ModuleWithProviders<VdkSharedNgrxProdModule> {
        return {
            ngModule: VdkSharedNgrxProdModule,
            providers: [
                { provide: RouterService, useClass: RouterServiceImpl },
                { provide: ComponentService, useClass: ComponentServiceImpl }
            ]
        };
    }
}
