/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * ** Part of Features Config.
 *
 *      - Should be provided when Module is initialized and only once.
 */
export interface WarningConfig {
    [WARNING_FEATURE_KEY]: {
        /**
         * ** Url that will open portal, where service request should be created.
         */
        serviceRequestUrl: string;
    };
}

/**
 * ** Key for the feature in Shared Features config object.
 */
const WARNING_FEATURE_KEY = 'warning';
