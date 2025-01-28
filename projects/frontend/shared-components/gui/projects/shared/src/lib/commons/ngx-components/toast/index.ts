/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable */

import { Type } from '@angular/core';
import { VdkToastComponent } from './toast.component';
import { VdkToastContainerComponent } from './toast-container.component';

export * from './toast.component';
export * from './toast-container.component';
export * from './toast.model';

export const TOAST_DIRECTIVES: Type<any>[] = [VdkToastContainerComponent, VdkToastComponent];
