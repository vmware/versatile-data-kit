/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { DatePipe } from '@angular/common';

import { TestBed } from '@angular/core/testing';

import { CallFake, CollectionsUtil } from '@versatiledatakit/shared';

import { DATA_PIPELINES_DATE_TIME_FORMAT, DataJobExecutionStatus } from '../../../../../../../model';

import { GridDataJobExecution } from '../../../model';

import { ExecutionsStatusCriteria } from './executions-status.criteria';

describe('ExecutionsStatusCriteria', () => {
    let datePipe: DatePipe;
    let dataJobExecutions: GridDataJobExecution[];

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [DatePipe]
        });

        datePipe = TestBed.inject(DatePipe);

        const aStartTime = new Date();
        const aEndTime = new Date(aStartTime.getTime() + 100);
        const bStartTime = new Date();
        const bEndTime = new Date(bStartTime.getTime() + 110);
        const cStartTime = new Date();
        const cEndTime = new Date(cStartTime.getTime() + 120);

        dataJobExecutions = [
            {
                id: 'aJob',
                startTimeFormatted: datePipe.transform(aStartTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                startTime: aStartTime.toISOString(),
                endTimeFormatted: datePipe.transform(aEndTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                endTime: aEndTime.toISOString(),
                duration: '100',
                jobVersion: '',
                status: DataJobExecutionStatus.SUCCEEDED
            },
            {
                id: 'bJob',
                startTimeFormatted: datePipe.transform(bStartTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                startTime: bStartTime.toISOString(),
                endTimeFormatted: datePipe.transform(bEndTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                endTime: bEndTime.toISOString(),
                duration: '110',
                jobVersion: '',
                status: DataJobExecutionStatus.RUNNING
            },
            {
                id: 'cJob',
                startTimeFormatted: datePipe.transform(cStartTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                startTime: cStartTime.toISOString(),
                endTimeFormatted: datePipe.transform(cEndTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                endTime: cEndTime.toISOString(),
                duration: '120',
                jobVersion: '',
                status: DataJobExecutionStatus.PLATFORM_ERROR
            }
        ];
    });

    describe('Methods::', () => {
        describe('|meetCriteria|', () => {
            it('should verify will return Array with aJob and bJob', () => {
                // Given
                const instance = new ExecutionsStatusCriteria('succeeded,running');

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual([dataJobExecutions[0], dataJobExecutions[1]]);
            });

            it('should verify will return Array with cJob', () => {
                // Given
                const instance = new ExecutionsStatusCriteria('platform_error');

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual([dataJobExecutions[2]]);
            });

            it('should verify will return empty Array', () => {
                // Given
                const instance = new ExecutionsStatusCriteria('user_error');

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual([]);
            });

            it('should verify will return Array with all Jobs when serialized status criteria is empty string', () => {
                // Given
                const instance = new ExecutionsStatusCriteria('');

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual(dataJobExecutions);
            });

            it('should verify will return Array with all Jobs when serialized status criteria is Nil', () => {
                // Given
                const instance = new ExecutionsStatusCriteria(null);

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual(dataJobExecutions);
            });

            it('should verify will return empty Array when Executions are Nil', () => {
                // Given
                const instance = new ExecutionsStatusCriteria('running');

                // When
                const res = instance.meetCriteria(null);

                // Then
                expect(res).toEqual([]);
            });

            it('should verify will return Array with all Jobs when serialized status deserialization fails', () => {
                // Given
                spyOn(CollectionsUtil, 'isStringWithContent').and.throwError(new Error('String validation fails'));
                const consoleErrorSpy = spyOn(console, 'error').and.callFake(CallFake);
                const instance = new ExecutionsStatusCriteria('running');

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual(dataJobExecutions);
                expect(consoleErrorSpy).toHaveBeenCalledWith(
                    `ExecutionsStatusCriteria: failed to deserialize Data Job Execution Statuses.`
                );
            });
        });
    });
});
