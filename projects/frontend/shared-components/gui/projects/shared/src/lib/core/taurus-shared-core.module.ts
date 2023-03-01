/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
	ModuleWithProviders,
	NgModule,
	Optional,
	SkipSelf
} from '@angular/core';

import { CookieService } from 'ngx-cookie-service';

import { NavigationService } from './navigation';

@NgModule({})
export class TaurusSharedCoreModule {
	/**
	 * ** Constructor.
	 */
	constructor(
		@Optional()
		@SkipSelf()
		readonly taurusSharedCoreModule: TaurusSharedCoreModule
	) {
		if (taurusSharedCoreModule) {
			throw new Error(
				'TaurusSharedCoreModule is already loaded. Import only once in root Module'
			);
		}
	}

	/**
	 * ** Provides TaurusSharedCore and all Services related to Taurus Core.
	 *
	 *      - Should be execute once for entire project.
	 */
	static forRoot(): ModuleWithProviders<TaurusSharedCoreModule> {
		return {
			ngModule: TaurusSharedCoreModule,
			providers: [CookieService, NavigationService]
		};
	}
}
