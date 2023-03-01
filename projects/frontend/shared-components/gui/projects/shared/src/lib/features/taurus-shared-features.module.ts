/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ModuleWithProviders, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { ClarityModule } from '@clr/angular';

import { VdkComponentsModule } from '../commons';

import { ToastsModule } from './toasts/toasts.module';

import { ErrorHandlerService } from './error-handler/service';

import { ToastService } from './toasts/service';

@NgModule({
	imports: [
		CommonModule,
		ClarityModule,
		VdkComponentsModule.forChild(),
		RouterModule,
		ToastsModule
	],
	exports: [ToastsModule]
})
export class TaurusSharedFeaturesModule {
	/**
	 * ** Provides TaurusSharedFeaturesModule and all Services related to Shared Module features.
	 *
	 *      - Should be invoke only once for entire project.
	 *      - Not inside FeatureModule (lazy loaded Module).
	 *      - In other modules import only taurus-shared-features.module.tTaurusSharedFeaturesModule.
	 */
	static forRoot(): ModuleWithProviders<TaurusSharedFeaturesModule> {
		return {
			ngModule: TaurusSharedFeaturesModule,
			providers: [ErrorHandlerService, ToastService]
		};
	}

	/**
	 * ** Provides TaurusSharedFeaturesModule.
	 *
	 *      - Should be invoke in FeatureModules (lazy loaded Modules).
	 */
	static forChild(): ModuleWithProviders<TaurusSharedFeaturesModule> {
		return {
			ngModule: TaurusSharedFeaturesModule
		};
	}
}
