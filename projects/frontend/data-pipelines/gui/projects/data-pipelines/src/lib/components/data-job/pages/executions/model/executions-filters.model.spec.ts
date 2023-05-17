/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
    FILTER_DURATION_KEY,
    FILTER_END_TIME_KEY,
    FILTER_ID_KEY,
    FILTER_START_TIME_KEY,
    FILTER_STATUS_KEY,
    FILTER_TIME_PERIOD_KEY,
    FILTER_TYPE_KEY,
    FILTER_VERSION_KEY,
    SORT_DURATION_KEY,
    SORT_END_TIME_KEY,
    SORT_ID_KEY,
    SORT_START_TIME_KEY,
    SORT_STATUS_KEY,
    SORT_TYPE_KEY,
    SORT_VERSION_KEY,
    SUPPORTED_EXECUTIONS_FILTER_CRITERIA,
    SUPPORTED_EXECUTIONS_SORT_CRITERIA
} from './executions-filters.model';

describe('SUPPORTED_EXECUTIONS_FILTER_CRITERIA', () => {
    it('should verify supported filter criteria are correct', () => {
        // Then
        expect(SUPPORTED_EXECUTIONS_FILTER_CRITERIA).toEqual([
            FILTER_TIME_PERIOD_KEY,
            FILTER_STATUS_KEY,
            FILTER_TYPE_KEY,
            FILTER_DURATION_KEY,
            FILTER_START_TIME_KEY,
            FILTER_END_TIME_KEY,
            FILTER_ID_KEY,
            FILTER_VERSION_KEY
        ]);
    });
});

describe('SUPPORTED_EXECUTIONS_SORT_CRITERIA', () => {
    it('should verify supported sort criteria are correct', () => {
        // Then
        expect(SUPPORTED_EXECUTIONS_SORT_CRITERIA).toEqual([
            SORT_STATUS_KEY,
            SORT_TYPE_KEY,
            SORT_DURATION_KEY,
            SORT_START_TIME_KEY,
            SORT_END_TIME_KEY,
            SORT_ID_KEY,
            SORT_VERSION_KEY
        ]);
    });
});
