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

describe('DataJobExecutionToGridDataJobExecution', () => {
    describe('Statics::', () => {
        describe('Methods::', () => {
            describe('|convertStatus|', () => {
                const params: Array<[string, string, DataJobExecutionStatus]> =
                    [
                        [
                            `${DataJobExecutionStatus.SUCCEEDED}`,
                            null,
                            DataJobExecutionStatus.SUCCEEDED,
                        ],
                        [
                            `${DataJobExecutionStatus.FINISHED}`,
                            null,
                            DataJobExecutionStatus.SUCCEEDED,
                        ],
                        [
                            `${DataJobExecutionStatus.FAILED}`,
                            'Platform error',
                            DataJobExecutionStatus.PLATFORM_ERROR,
                        ],
                        [
                            `${DataJobExecutionStatus.FAILED}`,
                            'Some exception message',
                            DataJobExecutionStatus.USER_ERROR,
                        ],
                        [
                            `${DataJobExecutionStatus.FAILED}`,
                            null,
                            DataJobExecutionStatus.FAILED,
                        ],
                        [
                            `Some new execution status`,
                            null,
                            `Some new execution status` as any,
                        ],
                    ];

                for (const [status, message, assertion] of params) {
                    it(`should verify for provided status "${status}" will return "${assertion}"`, () => {
                        // When
                        const returnedStatus =
                            /* eslint-disable @typescript-eslint/no-unsafe-argument */
                            DataJobExecutionToGridDataJobExecution.convertStatus(
                                status as any,
                                message,
                            );

                        // Then
                        expect(returnedStatus).toEqual(assertion);
                    });
                }
            });

            describe('|convertToDataJobExecution|', () => {
                it('should verify will convert object correctly', () => {
                    // Given
                    spyOn(Date, 'now').and.returnValue(1608036156085);

                    /* eslint-disable @typescript-eslint/naming-convention */
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
                    /* eslint-enable @typescript-eslint/naming-convention */

                    const convertedJobExecution =
                        DataJobExecutionToGridDataJobExecution.convertToDataJobExecution(
                            [
                                dataJobExecution,
                                {
                                    ...dataJobExecution,
                                    endTime: null,
                                },
                            ],
                        );

                    expect(convertedJobExecution.length).toEqual(2);
                    expect(convertedJobExecution).toEqual([
                        expectedObject,
                        { ...expectedObject, endTime: null, duration: '3d 2h' },
                    ]);
                });
            });

            describe('|getStatusColorsMap|', () => {
                it('should verify will return correct values', () => {
                    // When
                    const value =
                        DataJobExecutionToGridDataJobExecution.getStatusColorsMap();

                    // Then
                    expect(value).toEqual({
                        [DataJobExecutionStatus.SUBMITTED]: '#CCCCCC',
                        [DataJobExecutionStatus.RUNNING]: '#CCCCCC',
                        [DataJobExecutionStatus.SUCCEEDED]: '#5EB715',
                        [DataJobExecutionStatus.CANCELLED]: '#CCCCCC',
                        [DataJobExecutionStatus.SKIPPED]: '#CCCCCC',
                        [DataJobExecutionStatus.USER_ERROR]: '#F27963',
                        [DataJobExecutionStatus.PLATFORM_ERROR]: '#F8CF2A',
                    });
                });
            });

            describe('|resolveColor|', () => {
                it('should verify will resolve color from map', () => {
                    // When
                    const color =
                        DataJobExecutionToGridDataJobExecution.resolveColor(
                            DataJobExecutionStatus.SUCCEEDED,
                        );

                    // Then
                    expect(color).toEqual('#5EB715');
                });
            });
        });
    });
});
