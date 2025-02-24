/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';

import { CommonModule } from '@angular/common';
import { VdkSearchComponent } from './search.component';
import { ReactiveFormsModule } from '@angular/forms';

@NgModule({
    declarations: [VdkSearchComponent],
    imports: [CommonModule, ReactiveFormsModule],
    exports: [VdkSearchComponent],
    schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class VdkSearchModule {}
