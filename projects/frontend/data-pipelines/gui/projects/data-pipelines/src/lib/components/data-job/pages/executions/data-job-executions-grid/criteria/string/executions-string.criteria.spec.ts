/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DatePipe } from '@angular/common';

import { TestBed } from '@angular/core/testing';

import { DATA_PIPELINES_DATE_TIME_FORMAT, DataJobExecutionStatus, DataJobExecutionType } from '../../../../../../../model';

import { GridDataJobExecution } from '../../../model';

import { ExecutionsStringCriteria } from './executions-string.criteria';

describe('ExecutionsStringCriteria', () => {
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
                jobVersion: 'aJob-10',
                status: DataJobExecutionStatus.SUCCEEDED,
                type: DataJobExecutionType.SCHEDULED,
                opId: null
            },
            {
                id: 'bJob',
                startTimeFormatted: datePipe.transform(bStartTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                startTime: bStartTime.toISOString(),
                endTimeFormatted: datePipe.transform(bEndTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                endTime: bEndTime.toISOString(),
                duration: '110',
                jobVersion: 'bJob-11',
                status: DataJobExecutionStatus.RUNNING,
                type: DataJobExecutionType.SCHEDULED,
                opId: null
            },
            {
                id: 'cJob',
                startTimeFormatted: datePipe.transform(cStartTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                startTime: cStartTime.toISOString(),
                endTimeFormatted: datePipe.transform(cEndTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                endTime: cEndTime.toISOString(),
                duration: '120',
                jobVersion: 'cJob-12',
                status: DataJobExecutionStatus.PLATFORM_ERROR,
                type: DataJobExecutionType.MANUAL,
                opId: 'cJob_opId'
            }
        ];
    });

    describe('Methods::', () => {
        describe('|meetCriteria|', () => {
            it('should verify will return Array with aJob, bJob and cJob because match is partial and case insensitive', () => {
                // Given
                const instance = new ExecutionsStringCriteria('jobVersion', 'job');

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual(dataJobExecutions);
            });

            it('should verify will return Array with cJob', () => {
                // Given
                const instance = new ExecutionsStringCriteria('endTime', dataJobExecutions[2].endTime);

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual([dataJobExecutions[2]]);
            });

            it('should verify will return empty Array', () => {
                // Given
                const instance = new ExecutionsStringCriteria('id', 'aJobExecuted');

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual([]);
            });

            it('should verify will return only cJob because other opId are Nil', () => {
                // Given
                const instance = new ExecutionsStringCriteria('opId', 'opid');

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual([dataJobExecutions[2]]);
            });

            it('should verify will return Array with all Jobs when search value (query) is Nil', () => {
                // Given
                const instance = new ExecutionsStringCriteria('id', null);

                // When
                const res = instance.meetCriteria(dataJobExecutions);

                // Then
                expect(res).toEqual(dataJobExecutions);
            });

            it('should verify will return empty Array when Executions are Nil', () => {
                // Given
                const instance = new ExecutionsStringCriteria('startTimeFormatted', dataJobExecutions[0].startTimeFormatted);

                // When
                const res = instance.meetCriteria(null);

                // Then
                expect(res).toEqual([]);
            });
        });
    });
});
