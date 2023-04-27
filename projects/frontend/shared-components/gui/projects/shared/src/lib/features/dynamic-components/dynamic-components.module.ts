/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DynamicContainerComponent, DynamicContextComponent } from './components';

/**
 * ** Dynamic Components module
 *
 * @author gorankokin
 */
@NgModule({
    imports: [CommonModule],
    declarations: [DynamicContainerComponent, DynamicContextComponent],
    schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class DynamicComponentsModule {}
