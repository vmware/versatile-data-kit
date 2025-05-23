/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { Type } from '@angular/core';

import { RouterEffects } from '../../router/state/effects';

/**
 * ** Registry for Root Effects.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const SHARED_ROOT_EFFECTS: Array<Type<any>> = [RouterEffects];
