/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/naming-convention */

import { StatusDetails } from './data-job-base.model';

import { DataJobExecutionStatusDeprecated } from './data-job-executions.model';

/**
 * ** Data job details.
 *
 * @deprecated
 */
export interface DataJobDetails {
    job_name?: string;
    team?: string;
    description?: string;
    config?: DataJobConfigDetails;
}

/**
 * ** Data job config details.
 *
 * @deprecated
 */
export interface DataJobConfigDetails {
    schedule?: DataJobScheduleDetails;
    contacts?: DataJobContactsDetails;
}

/**
 * ** Data job execution.
 *
 * @deprecated
 */
export interface DataJobExecutionDetails {
    id: string;
    job_name: string;
    type: 'manual' | 'scheduled';
    status: DataJobExecutionStatusDeprecated;
    start_time: string;
    started_by: string;
    end_time: string;
    op_id: string;
    message: string;
    logs_url: string;
    deployment?: DataJobDeploymentDetails;
}

/**
 * ** Data job deployment.
 *
 * @deprecated
 */
export interface DataJobDeploymentDetails extends StatusDetails {
    id: string;
    job_version: string;
    mode: string;
    vdk_version: string;
    deployed_by: string;
    deployed_date: string;
    resources: {
        cpu_request: number;
        cpu_limit: number;
        memory_limit: number;
        memory_request: number;
    };
    contacts?: DataJobContactsDetails;
    schedule?: DataJobScheduleDetails;
}

/**
 * ** Data job schedule details.
 *
 * @deprecated
 */
export interface DataJobScheduleDetails {
    schedule_cron: string;
}

/**
 * ** Data job contacts details.
 *
 * @deprecated
 */
export interface DataJobContactsDetails {
    notified_on_job_deploy: string[];
    notified_on_job_failure_platform_error: string[];
    notified_on_job_failure_user_error: string[];
    notified_on_job_success: string[];
}
