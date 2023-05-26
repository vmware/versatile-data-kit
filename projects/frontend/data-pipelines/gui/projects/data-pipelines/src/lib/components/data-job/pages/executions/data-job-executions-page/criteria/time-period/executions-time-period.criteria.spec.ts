/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DatePipe } from '@angular/common';

import { TestBed } from '@angular/core/testing';

import { DATA_PIPELINES_DATE_TIME_FORMAT, DataJobExecutionStatus, DataJobExecutionType } from '../../../../../../../model';

import { GridDataJobExecution } from '../../../model';

import { ExecutionsTimePeriodCriteria } from './executions-time-period.criteria';

describe('ExecutionsTimePeriodCriteria', () => {
    let datePipe: DatePipe;
    let dataJobExecutions: GridDataJobExecution[];

    let aStartTime: Date;
    let bStartTime: Date;
    let cStartTime: Date;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [DatePipe]
        });

        datePipe = TestBed.inject(DatePipe);

        const currentTime = new Date();

        aStartTime = new Date(currentTime.getTime() + 10);
        const aEndTime = new Date(aStartTime.getTime() + 110);
        bStartTime = new Date(currentTime.getTime() + 20);
        const bEndTime = new Date(bStartTime.getTime() + 120);
        cStartTime = new Date(currentTime.getTime() + 30);
        const cEndTime = new Date(cStartTime.getTime() + 130);

        dataJobExecutions = [
            {
                id: 'aJob',
                startTimeFormatted: datePipe.transform(aStartTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                startTime: aStartTime.toISOString(),
                endTimeFormatted: datePipe.transform(aEndTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                endTime: aEndTime.toISOString(),
                duration: '100',
                jobVersion: '',
                status: DataJobExecutionStatus.SUCCEEDED,
                type: DataJobExecutionType.SCHEDULED
            },
            {
                id: 'bJob',
                startTimeFormatted: datePipe.transform(bStartTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                startTime: bStartTime.toISOString(),
                endTimeFormatted: datePipe.transform(bEndTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                endTime: bEndTime.toISOString(),
                duration: '110',
                jobVersion: '',
                status: DataJobExecutionStatus.RUNNING,
                type: DataJobExecutionType.SCHEDULED
            },
            {
                id: 'cJob',
                startTimeFormatted: datePipe.transform(cStartTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                startTime: cStartTime.toISOString(),
                endTimeFormatted: datePipe.transform(cEndTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                endTime: cEndTime.toISOString(),
                duration: '120',
                jobVersion: '',
                status: DataJobExecutionStatus.PLATFORM_ERROR,
                type: DataJobExecutionType.MANUAL
            }
        ];
    });

    describe('Methods::', () => {
        describe('|meetCriteria|', () => {
            it('should verify will return Array with aJob and bJob', () => {
                // Given
                const instance = new ExecutionsTimePeriodCriteria(aStartTime, bStartTime);

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual([dataJobExecutions[0], dataJobExecutions[1]]);
            });

            it('should verify will return Array with cJob', () => {
                // Given
                const instance = new ExecutionsTimePeriodCriteria(cStartTime, cStartTime);

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual([dataJobExecutions[2]]);
            });

            it('should verify will return empty Array when startTime is Nil', () => {
                // Given
                const instance = new ExecutionsTimePeriodCriteria(aStartTime, cStartTime);

                // When
                const res = instance.meetCriteria(dataJobExecutions.map((ex) => ({ ...ex, startTime: null })));

                // Then
                expect(res).toEqual([]);
            });

            it('should verify will return Array with all Jobs when from time is Nil', () => {
                // Given
                const instance = new ExecutionsTimePeriodCriteria(null, cStartTime);

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual(dataJobExecutions);
            });

            it('should verify will return Array with all Jobs when to time is Nil', () => {
                // Given
                const instance = new ExecutionsTimePeriodCriteria(aStartTime, null);

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual(dataJobExecutions);
            });

            it('should verify will return empty Array when Executions are Nil', () => {
                // Given
                const instance = new ExecutionsTimePeriodCriteria(aStartTime, cStartTime);

                // When
                const res = instance.meetCriteria(null);

                // Then
                expect(res).toEqual([]);
            });
        });
    });
});
