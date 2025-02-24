/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { CommonModule } from '@angular/common';
import { CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { VdkEmptyStatePlaceholderComponent } from './empty-state-placeholder.component';

@NgModule({
    imports: [CommonModule],
    declarations: [VdkEmptyStatePlaceholderComponent],
    exports: [VdkEmptyStatePlaceholderComponent],
    schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class VdkEmptyStatePlaceholderModule {}
