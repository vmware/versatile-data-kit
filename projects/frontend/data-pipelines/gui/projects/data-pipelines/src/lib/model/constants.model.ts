/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { InjectionToken } from '@angular/core';

import { DataPipelinesConfig } from './config.model';

/**
 * ** Injection Token for Data pipelines config.
 */
export const DATA_PIPELINES_CONFIGS = new InjectionToken<DataPipelinesConfig>(
    'DataPipelinesConfig',
);

/**
 * ** Team name constant used as key identifier in {@link ComponentState.requestParams}.
 */
export const TEAM_NAME_REQ_PARAM = 'team-name-req-param';

/**
 * ** Data Job name constant used as key identifier in {@link ComponentState.requestParams}.
 */
export const JOB_NAME_REQ_PARAM = 'job-name-req-param';

/**
 * ** Data Job deployment ID constant used as key identifier in {@link ComponentState.requestParams}.
 */
export const JOB_DEPLOYMENT_ID_REQ_PARAM = 'job-deployment-id-req-param';

/**
 * ** Data Job status constant used as key identifier in {@link ComponentState.requestParams}.
 */
export const JOB_STATUS_REQ_PARAM = 'job-status-req-param';

/**
 * ** Filter constant used as key identifier in {@link ComponentState.requestParams}.
 */
export const FILTER_REQ_PARAM = 'filter-req-param';

/**
 * ** Order constant used as key identifier in {@link ComponentState.requestParams}.
 */
export const ORDER_REQ_PARAM = 'order-req-param';

/**
 * ** Data Job details constant used as key identifier in {@link ComponentState.requestParams}.
 */
export const JOB_DETAILS_REQ_PARAM = 'job-details-req-param';

/**
 * ** Data Job state constant used as key identifier in {@link ComponentState.requestParams}.
 */
export const JOB_STATE_REQ_PARAM = 'job-state-req-param';

/**
 * ** Data Job state constant used as key identifier in {@link ComponentState.data}
 */
export const JOB_STATE_DATA_KEY = 'job-state-data-key';

/**
 * ** Data Jobs states constant used as key identifier in {@link ComponentState.data}
 */
export const JOBS_DATA_KEY = 'jobs-data-key';

/**
 * ** Data Job details constant used as key identifier in {@link ComponentState.data}
 */
export const JOB_DETAILS_DATA_KEY = 'job-details-data-key';

/**
 * ** Data Job Executions constant used as key identifier in {@link ComponentState.data}
 */
export const JOB_EXECUTIONS_DATA_KEY = 'job-executions-data-key';
