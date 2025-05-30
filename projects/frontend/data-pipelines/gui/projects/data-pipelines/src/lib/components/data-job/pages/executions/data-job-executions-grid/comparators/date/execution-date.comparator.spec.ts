/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { DatePipe } from '@angular/common';

import { TestBed } from '@angular/core/testing';

import { DATA_PIPELINES_DATE_TIME_FORMAT } from '../../../../../../../model';

import { GridDataJobExecution } from '../../../model';

import { ExecutionDateComparator } from './execution-date.comparator';

describe('ExecutionDateComparator', () => {
    let datePipe: DatePipe;
    let dataJobExecutions: GridDataJobExecution[];

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [DatePipe]
        });

        datePipe = TestBed.inject(DatePipe);

        const aStartTime = new Date();
        const bStartTime = new Date(aStartTime.getTime() + 100);
        const aEndTime = new Date();
        const bEndTime = new Date(aEndTime.getTime() + 110);

        dataJobExecutions = [
            {
                id: 'aJob',
                startTimeFormatted: datePipe.transform(aStartTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                startTime: aStartTime.toISOString(),
                endTimeFormatted: datePipe.transform(aEndTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                endTime: aEndTime.toISOString(),
                duration: '100',
                jobVersion: ''
            },
            {
                id: 'bJob',
                startTimeFormatted: datePipe.transform(bStartTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                startTime: bStartTime.toISOString(),
                endTimeFormatted: datePipe.transform(bEndTime, DATA_PIPELINES_DATE_TIME_FORMAT),
                endTime: bEndTime.toISOString(),
                duration: '110',
                jobVersion: ''
            }
        ];
    });

    describe('Properties::', () => {
        describe('|property|', () => {
            it('should verify value', () => {
                // Given
                const instance = new ExecutionDateComparator('endTime', 'ASC');

                // Then
                expect(instance.property).toEqual('endTime');
            });
        });

        describe('|direction|', () => {
            it('should verify value', () => {
                // Given
                const instance = new ExecutionDateComparator('startTime', 'ASC');

                // Then
                expect(instance.direction).toEqual('ASC');
            });
        });
    });

    describe('Methods::', () => {
        describe('|compare|', () => {
            it('should verify will return -100 because of ascending sort', () => {
                // Given
                const instance = new ExecutionDateComparator('startTime', 'ASC');

                // When
                const res = instance.compare(dataJobExecutions[0], dataJobExecutions[1]);

                // Then
                expect(res).toEqual(-100);
            });

            it('should verify will return 110 because of descending sort', () => {
                // Given
                const instance = new ExecutionDateComparator('endTime', 'DESC');

                // When
                const res = instance.compare(dataJobExecutions[0], dataJobExecutions[1]);

                // Then
                expect(res).toEqual(110);
            });
        });
    });
});
