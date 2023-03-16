/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { InjectionToken } from '@angular/core';

import { SharedFeaturesConfig } from '../_model';

/**
 * ** Injection token for Shared Features config.
 */
export const SHARED_FEATURES_CONFIG_TOKEN = new InjectionToken<SharedFeaturesConfig>('Shared Feature Config Token');
