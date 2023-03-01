/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataJobExecutionDurationComparator } from './execution-duration-comparator';

describe('DataJobExecutionDurationComparator', () => {
    describe('Methods::', () => {
        describe('|compare|', () => {
            it('should verify will return -10', () => {
                // Given
                const aStartTime = new Date();
                const aEndTime = new Date(aStartTime.getTime() + 100);
                const bStartTime = new Date();
                const bEndTime = new Date(bStartTime.getTime() + 110);
                const instance = new DataJobExecutionDurationComparator();

                // When
                const res = instance.compare(
                    {
                        id: 'aJob',
                        startTime: aStartTime.toISOString(),
                        endTime: aEndTime.toISOString(),
                        duration: '100',
                        jobVersion: '',
                    },
                    {
                        id: 'bJob',
                        startTime: bStartTime.toISOString(),
                        endTime: bEndTime.toISOString(),
                        duration: '110',
                        jobVersion: '',
                    }
                );

                // Then
                expect(res).toEqual(-10);
            });
        });
    });
});
