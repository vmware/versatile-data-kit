/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/naming-convention */

import { DirectionType } from '@vdk/shared';

import { DataJobExecution, DataJobExecutionStatus, GraphQLResponsePage } from './data-job-base.model';

export type DataJobExecutions = DataJobExecution[];

/**
 * ** Execution status.
 *
 * @deprecated
 */
// eslint-disable-next-line no-shadow
export enum DataJobExecutionStatusDeprecated {
    SUBMITTED = 'submitted',
    RUNNING = 'running',
    FINISHED = 'finished', // Keep for backward compatibility
    SUCCEEDED = 'succeeded',
    CANCELLED = 'cancelled',
    SKIPPED = 'skipped',
    FAILED = 'failed', // Keep for backward compatibility
    USER_ERROR = 'user_error',
    PLATFORM_ERROR = 'platform_error'
}

/**
 * ** Request variables fro DataJobs Executions jobsQuery GraphQL API.
 */
export interface DataJobExecutionsReqVariables {
    pageNumber?: number;
    pageSize?: number;
    filter?: DataJobExecutionFilter;
    order?: DataJobExecutionOrder;
}

export interface DataJobExecutionFilter {
    statusIn?: DataJobExecutionStatus[];
    jobNameIn?: string[];
    teamNameIn?: string[];
    startTimeGte?: string | Date;
    endTimeGte?: string | Date;
    startTimeLte?: string | Date;
    endTimeLte?: string | Date;
}

export interface DataJobExecutionOrder {
    property: keyof DataJobExecution;
    direction: DirectionType;
}

export type DataJobExecutionsPage = GraphQLResponsePage<DataJobExecution>;
