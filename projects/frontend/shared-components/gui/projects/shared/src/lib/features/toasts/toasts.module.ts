/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ClipboardModule } from 'ngx-clipboard';

import { ClarityModule } from '@clr/angular';

import { VdkComponentsModule } from '../../commons';

import { ToastsComponent } from './widget';

@NgModule({
    imports: [
        CommonModule,
        ClarityModule,
        VdkComponentsModule,
        ClipboardModule
    ],
    declarations: [
        ToastsComponent
    ],
    exports: [
        ToastsComponent
    ]
})
export class ToastsModule {
}
