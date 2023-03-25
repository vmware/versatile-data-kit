/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ServiceHttpErrorCodes } from '@versatiledatakit/shared';

import {
    TASK_LOAD_JOB_DETAILS,
    TASK_LOAD_JOB_EXECUTIONS,
    TASK_LOAD_JOB_STATE,
    TASK_LOAD_JOBS_STATE,
    TASK_UPDATE_JOB_DESCRIPTION,
    TASK_UPDATE_JOB_STATUS,
} from '../tasks';

// load tasks error codes

export const LOAD_JOB_ERROR_CODES: {
    [TASK_LOAD_JOB_STATE]: Readonly<
        Record<keyof ServiceHttpErrorCodes, string>
    >;
    [TASK_LOAD_JOB_DETAILS]: Readonly<
        Record<keyof ServiceHttpErrorCodes, string>
    >;
    [TASK_LOAD_JOB_EXECUTIONS]: Readonly<
        Record<keyof ServiceHttpErrorCodes, string>
    >;
} = {
    [TASK_LOAD_JOB_STATE]: null,
    [TASK_LOAD_JOB_DETAILS]: null,
    [TASK_LOAD_JOB_EXECUTIONS]: null,
};

export const LOAD_JOBS_ERROR_CODES: {
    [TASK_LOAD_JOBS_STATE]: Readonly<
        Record<keyof ServiceHttpErrorCodes, string>
    >;
} = {
    [TASK_LOAD_JOBS_STATE]: null,
};

// update tasks error codes

export const UPDATE_JOB_DETAILS_ERROR_CODES: {
    [TASK_UPDATE_JOB_STATUS]: Readonly<
        Record<keyof ServiceHttpErrorCodes, string>
    >;
    [TASK_UPDATE_JOB_DESCRIPTION]: Readonly<
        Record<keyof ServiceHttpErrorCodes, string>
    >;
} = {
    [TASK_UPDATE_JOB_STATUS]: null,
    [TASK_UPDATE_JOB_DESCRIPTION]: null,
};
