/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';

import { ClarityModule } from '@clr/angular';

import { CoreComponent } from './core.component';

const routes: Routes = [
    {
        path: '',
        component: CoreComponent
    }
];

@NgModule({
    declarations: [CoreComponent],
    imports: [RouterModule.forChild(routes), CommonModule, ClarityModule]
})
export class CoreModule {}
