/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DatePipe } from '@angular/common';

import { TestBed } from '@angular/core/testing';

import { DATA_PIPELINES_DATE_TIME_FORMAT } from '../../../../../../../model';

import { GridDataJobExecution } from '../../../model';

import { ExecutionDefaultComparator } from './execution-default.comparator';

describe('ExecutionDefaultComparator', () => {
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

        dataJobExecutions = [
            {
                id: 'aJob',
                startTimeFormatted: datePipe.transform(aStartTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                startTime: aStartTime.toISOString(),
                endTimeFormatted: datePipe.transform(aEndTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                endTime: aEndTime.toISOString(),
                duration: '100',
                jobVersion: 'version-10'
            },
            {
                id: 'bJob',
                startTimeFormatted: datePipe.transform(bStartTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                startTime: bStartTime.toISOString(),
                endTimeFormatted: datePipe.transform(bEndTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                endTime: bEndTime.toISOString(),
                duration: '110',
                jobVersion: 'version-11'
            }
        ];
    });

    describe('Properties::', () => {
        describe('|direction|', () => {
            it('should verify value', () => {
                // Given
                const instance = new ExecutionDefaultComparator('jobVersion', 'ASC');

                // Then
                expect(instance.property).toEqual('jobVersion');
                expect(instance.direction).toEqual('ASC');
            });
        });
    });

    describe('Methods::', () => {
        describe('|compare|', () => {
            it('should verify will return -1 because of ascending sort', () => {
                // Given
                const instance = new ExecutionDefaultComparator('jobVersion', 'ASC');

                // When
                const res = instance.compare(dataJobExecutions[0], dataJobExecutions[1]);

                // Then
                expect(res).toEqual(-1);
            });

            it('should verify will return 1 because of ascending sort', () => {
                // Given
                const instance = new ExecutionDefaultComparator('endTime', 'ASC');

                // When
                const res = instance.compare(dataJobExecutions[1], dataJobExecutions[0]);

                // Then
                expect(res).toEqual(1);
            });

            it('should verify will return 1 because of descending sort', () => {
                // Given
                const instance = new ExecutionDefaultComparator('jobVersion', 'DESC');

                // When
                const res = instance.compare(dataJobExecutions[0], dataJobExecutions[1]);

                // Then
                expect(res).toEqual(1);
            });

            it('should verify will return -1 because of descending sort', () => {
                // Given
                const instance = new ExecutionDefaultComparator('endTime', 'DESC');

                // When
                const res = instance.compare(dataJobExecutions[1], dataJobExecutions[0]);

                // Then
                expect(res).toEqual(-1);
            });

            it('should verify will return 0 because of ascending sort', () => {
                // Given
                const instance = new ExecutionDefaultComparator('startTime', 'ASC');

                // When
                const res = instance.compare(dataJobExecutions[0], dataJobExecutions[1]);

                // Then
                expect(res).toEqual(-0);
            });

            it('should verify will return 0 because of descending sort', () => {
                // Given
                const instance = new ExecutionDefaultComparator('startTime', 'DESC');

                // When
                const res = instance.compare(dataJobExecutions[0], dataJobExecutions[1]);

                // Then
                expect(res).toEqual(0);
            });
        });
    });
});
