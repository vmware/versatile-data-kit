/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

// load tasks

export const TASK_LOAD_JOB_STATE = 'load_job_state';

export const TASK_LOAD_JOB_DETAILS = 'load_job_details';

export const TASK_LOAD_JOB_EXECUTIONS = 'load_job_executions';

export type DataJobLoadTasks = typeof TASK_LOAD_JOB_STATE
    | typeof TASK_LOAD_JOB_DETAILS
    | typeof TASK_LOAD_JOB_EXECUTIONS;

// update tasks

export const TASK_UPDATE_JOB_DESCRIPTION = 'update_job_description';

export const TASK_UPDATE_JOB_STATUS = 'update_job_status';

export type DataJobUpdateTasks = typeof TASK_UPDATE_JOB_DESCRIPTION
    | typeof TASK_UPDATE_JOB_STATUS;
