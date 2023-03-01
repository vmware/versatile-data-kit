/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
    DataJobExecution,
    DataJobExecutionStatus,
    DataJobExecutionType,
} from '../../../../../model';
import {
    DataJobExecutionToGridDataJobExecution,
    GridDataJobExecution,
} from './data-job-execution';

describe('Test DataJobExecutionToGridDataJobExecution', () => {
    it('Convert object', () => {
        /* eslint-disable @typescript-eslint/naming-convention */
        const expectedObject: GridDataJobExecution = {
            jobName: 'test-job',
            status: DataJobExecutionStatus.PLATFORM_ERROR,
            type: DataJobExecutionType.MANUAL,
            startedBy: 'pmitev',
            startTime: '2020-12-12T10:10:10Z',
            endTime: '2020-12-12T11:11:11Z',
            duration: '1h 1m',
            message: 'Platform error',
            id: '123123123',
            opId: '123123123',
            jobVersion: 'jkdfgh',
            logsUrl: 'https://logs.com',
            deployment: {
                id: 'test',
                jobVersion: 'jkdfgh',
                mode: 'release',
                vdkVersion: '0.0.1',
                deployedDate: '2020-11-11T10:10:10Z',
                deployedBy: 'pmitev',
                resources: {
                    memoryLimit: 1000,
                    memoryRequest: 1000,
                    cpuLimit: 0.5,
                    cpuRequest: 0.5,
                },
                enabled: true,
                schedule: { scheduleCron: '12 * * * *' },
            },
        };

        const dataJobExecution: DataJobExecution = {
            jobName: 'test-job',
            status: DataJobExecutionStatus.FAILED,
            message: 'Platform error',
            type: DataJobExecutionType.MANUAL,
            id: '123123123',
            opId: '123123123',
            logsUrl: 'https://logs.com',
            startedBy: 'pmitev',
            startTime: '2020-12-12T10:10:10Z',
            endTime: '2020-12-12T11:11:11Z',
            deployment: {
                id: 'test',
                jobVersion: 'jkdfgh',
                mode: 'release',
                vdkVersion: '0.0.1',
                deployedDate: '2020-11-11T10:10:10Z',
                deployedBy: 'pmitev',
                resources: {
                    memoryLimit: 1000,
                    memoryRequest: 1000,
                    cpuLimit: 0.5,
                    cpuRequest: 0.5,
                },
                enabled: true,
                schedule: { scheduleCron: '12 * * * *' },
            },
        };
        /* eslint-enable @typescript-eslint/naming-convention */

        const convertedJobExecution =
            DataJobExecutionToGridDataJobExecution.convertToDataJobExecution([
                dataJobExecution,
            ]);

        expect(convertedJobExecution.length).toEqual(1);
        expect(convertedJobExecution[0]).toEqual(expectedObject);
    });
});
