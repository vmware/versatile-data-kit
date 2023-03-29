/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ModuleWithProviders, NgModule, Optional, SkipSelf } from '@angular/core';

import { CookieService } from 'ngx-cookie-service';

import { NavigationService } from './navigation';

@NgModule({})
export class VdkSharedCoreModule {
    /**
     * ** Constructor.
     */
    constructor(@Optional() @SkipSelf() readonly vdkSharedCoreModule: VdkSharedCoreModule) {
        if (vdkSharedCoreModule) {
            throw new Error('VdkSharedCoreModule is already loaded. Import only once in root Module');
        }
    }

    /**
     * ** Provides VDKSharedCore and all Services related to VDK Shared Core.
     *
     *      - Should be executed once for entire project.
     */
    static forRoot(): ModuleWithProviders<VdkSharedCoreModule> {
        return {
            ngModule: VdkSharedCoreModule,
            providers: [CookieService, NavigationService]
        };
    }
}
