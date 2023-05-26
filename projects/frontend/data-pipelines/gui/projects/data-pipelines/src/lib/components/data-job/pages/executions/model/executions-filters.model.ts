/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ClrDatagridSortOrder } from '@clr/angular';

import { FILTER_KEY, KeyValueTuple, SORT_KEY } from '../../../../../commons';

export const FILTER_TIME_PERIOD_KEY = 'timePeriod';
export const FILTER_STATUS_KEY = 'status';
export const FILTER_TYPE_KEY = 'type';
export const FILTER_DURATION_KEY = 'duration';
export const FILTER_START_TIME_KEY = 'startTime';
export const FILTER_END_TIME_KEY = 'endTime';
export const FILTER_ID_KEY = 'id';
export const FILTER_VERSION_KEY = 'jobVersion';

/**
 * ** Executions supported filter criteria types.
 */
export type ExecutionsFilterCriteria =
    | typeof FILTER_TIME_PERIOD_KEY
    | typeof FILTER_STATUS_KEY
    | typeof FILTER_TYPE_KEY
    | typeof FILTER_DURATION_KEY
    | typeof FILTER_START_TIME_KEY
    | typeof FILTER_END_TIME_KEY
    | typeof FILTER_ID_KEY
    | typeof FILTER_VERSION_KEY;

/**
 * ** Executions filter pair with its corresponding value in Tuple.
 */
export type ExecutionsFilterPairs<K extends string = ExecutionsFilterCriteria> = KeyValueTuple<K, string>;

/**
 * ** Executions grid filter with its value.
 */
export type ExecutionsGridFilter<K extends string = ExecutionsFilterCriteria> = { property: K; value: string };

/**
 * ** Executions supported filter criteria.
 */
export const SUPPORTED_EXECUTIONS_FILTER_CRITERIA: ExecutionsFilterCriteria[] = [
    FILTER_TIME_PERIOD_KEY,
    FILTER_STATUS_KEY,
    FILTER_TYPE_KEY,
    FILTER_DURATION_KEY,
    FILTER_START_TIME_KEY,
    FILTER_END_TIME_KEY,
    FILTER_ID_KEY,
    FILTER_VERSION_KEY
];

export const SORT_STATUS_KEY = 'status';
export const SORT_TYPE_KEY = 'type';
export const SORT_DURATION_KEY = 'duration';
export const SORT_START_TIME_KEY = 'startTime';
export const SORT_END_TIME_KEY = 'endTime';
export const SORT_ID_KEY = 'id';
export const SORT_VERSION_KEY = 'jobVersion';

/**
 * ** Executions supported sort criteria types.
 */
export type ExecutionsSortCriteria =
    | typeof SORT_STATUS_KEY
    | typeof SORT_TYPE_KEY
    | typeof SORT_DURATION_KEY
    | typeof SORT_START_TIME_KEY
    | typeof SORT_END_TIME_KEY
    | typeof SORT_ID_KEY
    | typeof SORT_VERSION_KEY;

/**
 * ** Executions sort pair with its corresponding value in Tuple.
 */
export type ExecutionsSortPairs = KeyValueTuple<ExecutionsSortCriteria, ClrDatagridSortOrder>;

/**
 * ** Executions supported sort criteria.
 */
export const SUPPORTED_EXECUTIONS_SORT_CRITERIA: ExecutionsSortCriteria[] = [
    SORT_STATUS_KEY,
    SORT_TYPE_KEY,
    SORT_DURATION_KEY,
    SORT_START_TIME_KEY,
    SORT_END_TIME_KEY,
    SORT_ID_KEY,
    SORT_VERSION_KEY
];

/**
 * ** Executions object that holds filter and sort criteria and their corresponding values.
 */
export type ExecutionsFilterSortObject = Record<typeof FILTER_KEY | typeof SORT_KEY, string>;
