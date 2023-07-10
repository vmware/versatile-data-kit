/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NavigationExtras } from '@angular/router';

/**
 * ** System Event ID for navigation trigger.
 *
 *   - Send event [BLOCKING]
 *   - Every Handler should return Promise.
 *
 *   - Payload {@link SystemEventNavigatePayload}
 */
export const SE_NAVIGATE = 'SE_Navigate';

/**
 * ** System Event ID for location change through {@link @angular/common/Location}.
 *
 *   - Post event [NON-BLOCKING]
 *   - Every Handler could either consume event as void (return nothing) or return Promise.
 *   - Execution is in queue using setTimeout of 0.
 *
 *   - Payload {@link SystemEventLocationChangePayload}
 */
export const SE_LOCATION_CHANGE = 'SE_Location_Change';

/**
 * ** System Event that could be consumed by Handlers.
 * <p>
 *   - Must return a Promise!
 *
 *   - Handlers will listen for all Events in the System.
 *   - They could be BLOCKING and NON-BLOCKING.
 *
 *   - Payload {any}
 */
export const SE_ALL_EVENTS = '*';

// events payload types

/**
 * ** Payload send whenever {@link SE_NAVIGATE} event is fired.
 */
export interface SystemEventNavigatePayload {
    url: string | string[];
    extras?: NavigationExtras;
}

/**
 * ** Payload post whenever {@link SE_LOCATION_CHANGE} event is fired.
 */
export interface SystemEventLocationChangePayload {
    /**
     * ** Url in string format.
     *
     *      - e.g. '/pathname/path-param_1/path-param_2?query-param-1=value_1&query-param-2=value_2'
     */
    url: string;
    /**
     * ** Dynamic path params in key-value map format.
     */
    params: { [key: string]: string };
    /**
     * ** Dynamic path params serialized in string format.
     *
     *      - e.g. '/pathname/path-param_1/path-param_2'
     */
    paramsSerialized: string;
    /**
     * ** Dynamic query params in key-value map format.
     */
    queryParams: { [key: string]: string };
    /**
     * ** Dynamic query params serialized in string format.
     *
     *      - e.g. 'query-param-1=value_1&query-param-2=value_2'
     */
    queryParamsSerialized: string;
}
