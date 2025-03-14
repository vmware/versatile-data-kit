/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule, ModuleWithProviders } from '@angular/core';

import { VdkSimpleTranslateService } from './simple-translate.service';
import { VdkSimpleTranslatePipe } from './simple-translate.pipe';

@NgModule({
    declarations: [VdkSimpleTranslatePipe],
    exports: [VdkSimpleTranslatePipe]
})
export class VdkSimpleTranslateModule {
    static forRoot(): ModuleWithProviders<VdkSimpleTranslateModule> {
        return {
            ngModule: VdkSimpleTranslateModule,
            providers: [VdkSimpleTranslateService]
        };
    }
}
