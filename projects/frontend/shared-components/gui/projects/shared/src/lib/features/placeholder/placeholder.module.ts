/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule, NO_ERRORS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ClarityModule } from '@clr/angular';

import { EmptyStateComponent, PlaceholderComponent } from './components';

/**
 * ** Placeholder module
 */
@NgModule({
    imports: [CommonModule, ClarityModule],
    declarations: [EmptyStateComponent, PlaceholderComponent],
    exports: [EmptyStateComponent, PlaceholderComponent],
    schemas: [NO_ERRORS_SCHEMA]
})
export class PlaceholderModule {}
