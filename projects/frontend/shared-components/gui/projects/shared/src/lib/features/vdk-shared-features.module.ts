/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ModuleWithProviders, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { ClarityModule } from '@clr/angular';

import { SharedFeaturesConfig } from './_model';

import { VdkSharedComponentsModule } from '../commons';

import { SHARED_FEATURES_CONFIG_TOKEN } from './_token';

import { PlaceholderModule } from './placeholder/placeholder.module';

import { WarningModule } from './warning/warning.module';

import { ToastsModule } from './toasts/toasts.module';
import { ToastService } from './toasts/service';

import { ErrorHandlerService } from './error-handler/services';

import { DirectivesModule } from './directives/directives.module';

import { PipesModule } from './pipes/pipes.module';

@NgModule({
    imports: [
        CommonModule,
        RouterModule,
        ClarityModule,
        VdkSharedComponentsModule.forChild(),
        ToastsModule,
        WarningModule,
        PlaceholderModule,
        DirectivesModule,
        PipesModule
    ],
    exports: [ToastsModule, WarningModule, PlaceholderModule, DirectivesModule, PipesModule]
})
export class VdkSharedFeaturesModule {
    /**
     * ** Provides VdkSharedFeaturesModule and all Services related to Shared Module features.
     *
     *      - Should be invoked only once for entire project.
     *      - Not inside FeatureModule (lazy loaded Module).
     *      - In other modules import only VdkSharedFeaturesModule or VdkSharedFeaturesModule.forChild().
     */
    static forRoot(featuresConfig?: SharedFeaturesConfig): ModuleWithProviders<VdkSharedFeaturesModule> {
        return {
            ngModule: VdkSharedFeaturesModule,
            providers: [{ provide: SHARED_FEATURES_CONFIG_TOKEN, useValue: featuresConfig ?? {} }, ErrorHandlerService, ToastService]
        };
    }

    /**
     * ** Provides VdkSharedFeaturesModule.
     *
     *      - Should be invoked in FeatureModules (lazy loaded Modules).
     */
    static forChild(): ModuleWithProviders<VdkSharedFeaturesModule> {
        return {
            ngModule: VdkSharedFeaturesModule
        };
    }
}
