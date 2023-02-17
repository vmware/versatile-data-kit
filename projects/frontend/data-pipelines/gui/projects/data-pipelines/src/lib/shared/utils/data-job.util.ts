/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil } from '@vdk/shared';

import {
    DataJobDeployment,
    DataJobExecution,
    DataJobExecutionDetails,
    DataJobExecutionStatus,
    DataJobExecutionStatusDeprecated,
    DataJobExecutionType
} from '../../model';

/**
 * ** Utils for Data Job.
 */
export class DataJobUtil {
    /**
     * ** Predicate for Job Running.
     */
    static isJobRunningPredicate(jobExecution: DataJobExecution | DataJobExecutionDetails): boolean {
        return (jobExecution as DataJobExecution).status === DataJobExecutionStatus.RUNNING ||
            (jobExecution as DataJobExecution).status === DataJobExecutionStatus.SUBMITTED ||
            (jobExecution as DataJobExecutionDetails).status === DataJobExecutionStatusDeprecated.RUNNING ||
            (jobExecution as DataJobExecutionDetails).status === DataJobExecutionStatusDeprecated.SUBMITTED;
    }

    /**
     * ** Find if some Job is running in provided Executions.
     */
    static isJobRunning(jobExecutions: DataJobExecution[] | DataJobExecutionDetails[]): boolean {
        // eslint-disable-next-line @typescript-eslint/unbound-method
        return jobExecutions.findIndex(DataJobUtil.isJobRunningPredicate) !== -1;
    }

    static convertFromExecutionDetailsToExecutionState(jobExecutionDetails: DataJobExecutionDetails): DataJobExecution {
        if (CollectionsUtil.isNil(jobExecutionDetails)) {
            return {
                id: null
            };
        }

        const execution: DataJobExecution = {
            id: jobExecutionDetails.id,
            jobName: jobExecutionDetails.job_name,
            opId: jobExecutionDetails.op_id,
            status: jobExecutionDetails.status.toUpperCase() as DataJobExecutionStatus,
            startedBy: jobExecutionDetails.started_by,
            startTime: jobExecutionDetails.start_time,
            endTime: jobExecutionDetails.end_time,
            message: jobExecutionDetails.message,
            type: jobExecutionDetails.type.toUpperCase() as DataJobExecutionType,
            logsUrl: jobExecutionDetails.logs_url,
            deployment: {
                schedule: {},
                resources: {}
            } as DataJobDeployment
        };

        if (CollectionsUtil.isLiteralObject(jobExecutionDetails.deployment)) {
            execution.deployment.id = jobExecutionDetails.deployment.id;
            execution.deployment.enabled = jobExecutionDetails.deployment.enabled;
            execution.deployment.jobVersion = jobExecutionDetails.deployment.job_version;
            execution.deployment.vdkVersion = jobExecutionDetails.deployment.vdk_version;
            execution.deployment.mode = jobExecutionDetails.deployment.mode;
            execution.deployment.deployedDate = jobExecutionDetails.deployment.deployed_date;
            execution.deployment.deployedBy = jobExecutionDetails.deployment.deployed_by;

            if (CollectionsUtil.isLiteralObject(jobExecutionDetails.deployment.schedule)) {
                execution.deployment.schedule.scheduleCron = jobExecutionDetails.deployment.schedule.schedule_cron;
            }

            if (CollectionsUtil.isLiteralObject(jobExecutionDetails.deployment.resources)) {
                execution.deployment.resources.cpuRequest = jobExecutionDetails.deployment.resources.cpu_request;
                execution.deployment.resources.cpuLimit = jobExecutionDetails.deployment.resources.cpu_limit;
                execution.deployment.resources.memoryRequest = jobExecutionDetails.deployment.resources.memory_request;
                execution.deployment.resources.memoryLimit = jobExecutionDetails.deployment.resources.memory_limit;
            }
        }

        return execution;
    }
}
