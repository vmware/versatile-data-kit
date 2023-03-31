/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { WarningConfig } from '../warning';
import { PlaceholderConfig } from '../placeholder';

/**
 * ** Configuration that should be provided when Shared Features module is injected in the root of the application.
 */
export type SharedFeaturesConfig = WarningConfig & PlaceholderConfig;
