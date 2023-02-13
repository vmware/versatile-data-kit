/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/naming-convention */

export interface StatusDetails {
    enabled: boolean;
}

export interface GraphQLResponsePage<T> {
    content?: T[];
    totalItems?: number;
    totalPages?: number;
}

// Deployment

export interface BaseDataJobDeployment<E extends DataJobExecution = DataJobExecution> extends StatusDetails {
    id: string;
    contacts?: DataJobContacts;
    jobVersion?: string;
    deployedDate?: string;
    deployedBy?: string;
    mode?: string;
    resources?: DataJobResources;
    schedule?: DataJobSchedule;
    vdkVersion?: string;
    status?: DataJobDeploymentStatus;
    executions?: E[];
}

export enum DataJobDeploymentStatus {
    NONE = 'NONE',
    SUCCESS = 'SUCCESS',
    PLATFORM_ERROR = 'PLATFORM_ERROR',
    USER_ERROR = 'USER_ERROR'
}

export interface DataJobContacts {
    notifiedOnJobFailureUserError: string[];
    notifiedOnJobFailurePlatformError: string[];
    notifiedOnJobSuccess: string[];
    notifiedOnJobDeploy: string[];
}

export interface DataJobSchedule {
    scheduleCron?: string;
    nextRunEpochSeconds?: number;
}

export interface DataJobResources {
    cpuLimit: number;
    cpuRequest: number;
    memoryLimit: number;
    memoryRequest: number;
    ephemeralStorageLimit?: number;
    ephemeralStorageRequest?: number;
    netBandwidthLimit?: number;
}

// Execution

export interface DataJobExecution {
    id: string;
    type?: DataJobExecutionType;
    jobName?: string;
    status?: DataJobExecutionStatus;
    startTime?: string;
    endTime?: string;
    startedBy?: string;
    message?: string;
    opId?: string;
    logsUrl?: string;
    deployment?: BaseDataJobDeployment;
}

export enum DataJobExecutionType {
    MANUAL = 'MANUAL',
    SCHEDULED = 'SCHEDULED'
}

/**
 * ** Execution Status.
 */
export enum DataJobExecutionStatus {
    SUBMITTED = 'SUBMITTED',
    RUNNING = 'RUNNING',
    FINISHED = 'FINISHED', // Keep for backward compatibility
    SUCCEEDED = 'SUCCEEDED',
    CANCELLED = 'CANCELLED',
    SKIPPED = 'SKIPPED',
    FAILED = 'FAILED', // Keep for backward compatibility
    USER_ERROR = 'USER_ERROR',
    PLATFORM_ERROR = 'PLATFORM_ERROR'
}
