/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/naming-convention */

import {
    DataJobExecution,
    DataJobExecutionDetails,
    DataJobExecutionStatus,
    DataJobExecutionStatusDeprecated,
    DataJobExecutionType
} from '../../model';

import { DataJobUtil } from './data-job.util';

describe('DataJobUtil', () => {
    describe('|isJobRunningPredicate|', () => {
        it('should verify will return true if status is RUNNING', () => {
            // Given
            const execution: DataJobExecutionDetails = {
                status: DataJobExecutionStatusDeprecated.RUNNING
            } as any;

            // When
            const response = DataJobUtil.isJobRunningPredicate(execution);

            // Then
            expect(response).toBeTrue();
        });

        it('should verify will return true if status is SUBMITTED', () => {
            // Given
            const execution: DataJobExecutionDetails = {
                status: DataJobExecutionStatusDeprecated.SUBMITTED
            } as any;

            // When
            const response = DataJobUtil.isJobRunningPredicate(execution);

            // Then
            expect(response).toBeTrue();
        });

        it('should verify will return false if status is different from RUNNING or SUBMITTED', () => {
            // Given
            const execution1: DataJobExecutionDetails = {
                status: DataJobExecutionStatusDeprecated.USER_ERROR
            } as any;
            const execution2: DataJobExecutionDetails = {
                status: DataJobExecutionStatusDeprecated.SKIPPED
            } as any;
            const execution3: DataJobExecutionDetails = {
                status: DataJobExecutionStatusDeprecated.PLATFORM_ERROR
            } as any;
            const execution4: DataJobExecutionDetails = {
                status: DataJobExecutionStatusDeprecated.SUCCEEDED
            } as any;

            // When
            const response1 = DataJobUtil.isJobRunningPredicate(execution1);
            const response2 = DataJobUtil.isJobRunningPredicate(execution2);
            const response3 = DataJobUtil.isJobRunningPredicate(execution3);
            const response4 = DataJobUtil.isJobRunningPredicate(execution4);

            // Then
            expect(response1).toBeFalse();
            expect(response2).toBeFalse();
            expect(response3).toBeFalse();
            expect(response4).toBeFalse();
        });
    });

    describe('|isJobRunning|', () => {
        it('should verify will invoke correct method', () => {
            // Given
            const spy = spyOn(DataJobUtil, 'isJobRunningPredicate').and.callThrough();
            const executions: DataJobExecutionDetails[] = [{ status: DataJobExecutionStatusDeprecated.RUNNING }] as any;

            // When
            DataJobUtil.isJobRunning(executions);

            // Then
            expect(spy.calls.argsFor(0)[0]).toEqual(executions[0]);
        });

        it('should verify will invoke correct method until find RUNNING or SUBMITTED status', () => {
            // Given
            const spy = spyOn(DataJobUtil, 'isJobRunningPredicate').and.callThrough();
            const executions: DataJobExecutionDetails[] = [
                { status: DataJobExecutionStatusDeprecated.FAILED },
                { status: DataJobExecutionStatusDeprecated.PLATFORM_ERROR },
                { status: DataJobExecutionStatusDeprecated.SUBMITTED },
                { status: DataJobExecutionStatusDeprecated.RUNNING }
            ] as any;

            // When
            DataJobUtil.isJobRunning(executions);

            // Then
            expect(spy).toHaveBeenCalledTimes(3);
            expect(spy.calls.argsFor(0)[0]).toEqual(executions[0]);
            expect(spy.calls.argsFor(1)[0]).toEqual(executions[1]);
            expect(spy.calls.argsFor(2)[0]).toEqual(executions[2]);
        });

        it('should verify will invoke correct method with all elements no RUNNING or SUBMITTED status', () => {
            // Given
            const spy = spyOn(DataJobUtil, 'isJobRunningPredicate').and.callThrough();
            const executions: DataJobExecutionDetails[] = [
                { status: DataJobExecutionStatusDeprecated.FAILED },
                { status: DataJobExecutionStatusDeprecated.PLATFORM_ERROR },
                { status: DataJobExecutionStatusDeprecated.SUCCEEDED },
                { status: DataJobExecutionStatusDeprecated.SKIPPED }
            ] as any;

            // When
            DataJobUtil.isJobRunning(executions);

            // Then
            expect(spy).toHaveBeenCalledTimes(4);
            expect(spy.calls.argsFor(0)[0]).toEqual(executions[0]);
            expect(spy.calls.argsFor(1)[0]).toEqual(executions[1]);
            expect(spy.calls.argsFor(2)[0]).toEqual(executions[2]);
            expect(spy.calls.argsFor(3)[0]).toEqual(executions[3]);
        });
    });

    describe('|convertFromExecutionDetailsToExecutionState|', () => {
        let executionDetails: DataJobExecutionDetails;
        let expectedExecution: DataJobExecution;

        beforeEach(() => {
            executionDetails = {
                id: 'id001',
                job_name: 'job001',
                type: 'manual',
                status: DataJobExecutionStatusDeprecated.SUBMITTED,
                start_time: new Date().toISOString(),
                started_by: 'aUserov',
                end_time: new Date().toISOString(),
                op_id: 'op001',
                message: 'message001',
                logs_url: 'http://url',
                deployment: {
                    schedule: {
                        schedule_cron: '5 5 5 5 *'
                    },
                    id: 'id002',
                    enabled: true,
                    job_version: '002',
                    mode: 'test_mode',
                    vdk_version: '002',
                    resources: {
                        memory_limit: 1000,
                        memory_request: 1000,
                        cpu_limit: 0.5,
                        cpu_request: 0.5
                    },
                    deployed_date: '2020-11-11T10:10:10Z',
                    deployed_by: 'pmitev'
                }
            };
            expectedExecution = {
                id: 'id001',
                jobName: 'job001',
                type: DataJobExecutionType.MANUAL,
                status: DataJobExecutionStatus.SUBMITTED,
                startTime: executionDetails.start_time,
                startedBy: 'aUserov',
                endTime: executionDetails.end_time,
                opId: 'op001',
                message: 'message001',
                logsUrl: 'http://url',
                deployment: {
                    schedule: {
                        scheduleCron: '5 5 5 5 *'
                    },
                    id: 'id002',
                    enabled: true,
                    jobVersion: '002',
                    mode: 'test_mode',
                    vdkVersion: '002',
                    resources: {
                        memoryLimit: 1000,
                        memoryRequest: 1000,
                        cpuLimit: 0.5,
                        cpuRequest: 0.5
                    },
                    deployedDate: '2020-11-11T10:10:10Z',
                    deployedBy: 'pmitev'
                }
            };
        });

        it('should verify will return empty execution when null and undefined provided', () => {
            // When
            const res1 = DataJobUtil.convertFromExecutionDetailsToExecutionState(null);
            const res2 = DataJobUtil.convertFromExecutionDetailsToExecutionState(undefined);

            // Then
            expect(res1).toEqual({ id: null });
            expect(res2).toEqual({ id: null });
        });

        it('should verify will correctly convert case 1', () => {
            // When
            const converted = DataJobUtil.convertFromExecutionDetailsToExecutionState(executionDetails);

            // Then
            expect(converted).toEqual(expectedExecution);
        });

        it('should verify will correctly convert case 2', () => {
            // Given
            delete executionDetails.deployment.resources;
            expectedExecution.deployment.resources = {} as any;

            // When
            const converted = DataJobUtil.convertFromExecutionDetailsToExecutionState(executionDetails);

            // Then
            expect(converted).toEqual(expectedExecution);
        });

        it('should verify will correctly convert case 3', () => {
            // Given
            delete executionDetails.deployment.schedule;
            expectedExecution.deployment.schedule = {} as any;

            // When
            const converted = DataJobUtil.convertFromExecutionDetailsToExecutionState(executionDetails);

            // Then
            expect(converted).toEqual(expectedExecution);
        });

        it('should verify will correctly convert case 4', () => {
            // Given
            delete executionDetails.deployment;
            expectedExecution.deployment = {
                schedule: {},
                resources: {}
            } as any;

            // When
            const converted = DataJobUtil.convertFromExecutionDetailsToExecutionState(executionDetails);

            // Then
            expect(converted).toEqual(expectedExecution);
        });
    });
});
