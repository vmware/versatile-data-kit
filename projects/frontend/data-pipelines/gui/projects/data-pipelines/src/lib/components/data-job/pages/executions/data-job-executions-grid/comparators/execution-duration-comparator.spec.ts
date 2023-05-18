/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DatePipe } from '@angular/common';

import { TestBed } from '@angular/core/testing';

import { CollectionsUtil } from '@versatiledatakit/shared';

import { DATA_PIPELINES_DATE_TIME_FORMAT } from '../../../../../../model';

import { DataJobExecutionDurationComparator } from './execution-duration-comparator';

describe('DataJobExecutionDurationComparator', () => {
    let property: string;
    let datePipe: DatePipe;

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [DatePipe]
        });

        datePipe = TestBed.inject(DatePipe);

        property = CollectionsUtil.generateRandomString();
    });

    describe('Properties::', () => {
        describe('|property|', () => {
            it('should verify value', () => {
                // Given
                const instance = new DataJobExecutionDurationComparator(property);

                // Then
                expect(instance.property).toEqual(property);
            });
        });
    });

    describe('Methods::', () => {
        describe('|compare|', () => {
            it('should verify will return -10', () => {
                // Given
                const aStartTime = new Date();
                const aEndTime = new Date(aStartTime.getTime() + 100);
                const bStartTime = new Date();
                const bEndTime = new Date(bStartTime.getTime() + 110);
                const instance = new DataJobExecutionDurationComparator(property);

                // When
                const res = instance.compare(
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
                );

                // Then
                expect(res).toEqual(-10);
            });
        });
    });
});
