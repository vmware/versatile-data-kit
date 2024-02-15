/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021-2024 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ClipboardModule } from 'ngx-clipboard';

import { ClarityModule } from '@clr/angular';

import { VdkSharedComponentsModule } from '../../commons';

import { ToastsComponent } from './widget';

@NgModule({
    imports: [CommonModule, ClarityModule, VdkSharedComponentsModule, ClipboardModule],
    declarations: [ToastsComponent],
    exports: [ToastsComponent]
})
export class ToastsModule {}
