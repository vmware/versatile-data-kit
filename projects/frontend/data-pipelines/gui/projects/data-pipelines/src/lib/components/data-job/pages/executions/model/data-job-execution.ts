/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DatePipe } from '@angular/common';

import { FormatDeltaPipe } from '../../../../../shared/pipes';

import { DATA_PIPELINES_DATE_TIME_FORMAT, DataJobExecution, DataJobExecutions, DataJobExecutionStatus } from '../../../../../model';

export interface GridDataJobExecution extends DataJobExecution {
    duration: string;
    jobVersion: string;
    startTimeFormatted: string;
    endTimeFormatted: string;
}

export class DataJobExecutionToGridDataJobExecution {
    static convertStatus(jobStatus: DataJobExecutionStatus, message: string): DataJobExecutionStatus {
        switch (`${jobStatus}`.toUpperCase()) {
            case DataJobExecutionStatus.SUCCEEDED:
            case DataJobExecutionStatus.FINISHED:
                return DataJobExecutionStatus.SUCCEEDED;
            case DataJobExecutionStatus.FAILED:
                if (message) {
                    return message === 'Platform error' ? DataJobExecutionStatus.PLATFORM_ERROR : DataJobExecutionStatus.USER_ERROR;
                } else {
                    return DataJobExecutionStatus.FAILED;
                }
            default:
                return jobStatus;
        }
    }

    static convertToDataJobExecution(datePipe: DatePipe) {
        return (dataJobExecution: DataJobExecutions): GridDataJobExecution[] => {
            const formatDeltaPipe = new FormatDeltaPipe();

            return dataJobExecution.reduce((accumulator, execution) => {
                accumulator.push({
                    status: DataJobExecutionToGridDataJobExecution.convertStatus(execution.status, execution.message),
                    type: execution.type,
                    duration: formatDeltaPipe.transform(execution),
                    startTime: execution.startTime,
                    startTimeFormatted: execution.startTime
                        ? datePipe.transform(execution.startTime, DATA_PIPELINES_DATE_TIME_FORMAT, 'UTC')
                        : '',
                    endTime: execution.endTime ? execution.endTime : null,
                    endTimeFormatted: execution.endTime
                        ? datePipe.transform(execution.endTime, DATA_PIPELINES_DATE_TIME_FORMAT, 'UTC')
                        : '',
                    logsUrl: execution.logsUrl,
                    startedBy: execution.startedBy,
                    id: execution.id,
                    jobName: execution.jobName,
                    opId: execution.opId,
                    jobVersion: execution.deployment.jobVersion,
                    deployment: execution.deployment,
                    message: execution.message
                });

                return accumulator;
            }, [] as GridDataJobExecution[]);
        };
    }

    static getStatusColorsMap() {
        return {
            [DataJobExecutionStatus.SUBMITTED]: '#CCCCCC',
            [DataJobExecutionStatus.RUNNING]: '#CCCCCC',
            [DataJobExecutionStatus.SUCCEEDED]: '#5EB715',
            [DataJobExecutionStatus.CANCELLED]: '#CCCCCC',
            [DataJobExecutionStatus.SKIPPED]: '#CCCCCC',
            [DataJobExecutionStatus.USER_ERROR]: '#F27963',
            [DataJobExecutionStatus.PLATFORM_ERROR]: '#F8CF2A'
        };
    }

    static resolveColor(key: string): string {
        return DataJobExecutionToGridDataJobExecution.getStatusColorsMap()[key] as string;
    }
}
