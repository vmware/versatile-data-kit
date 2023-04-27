/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule, NO_ERRORS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { ClarityModule } from '@clr/angular';

import { ConfirmationComponent, ConfirmationContainerComponent } from './components';

/**
 * ** Confirmation module
 *
 * @author gorankokin
 */
@NgModule({
    imports: [CommonModule, ClarityModule, FormsModule],
    declarations: [ConfirmationContainerComponent, ConfirmationComponent],
    schemas: [NO_ERRORS_SCHEMA]
})
export class ConfirmationModule {}
