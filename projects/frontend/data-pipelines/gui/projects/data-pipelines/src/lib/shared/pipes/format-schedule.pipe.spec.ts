/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { FormatSchedulePipe } from './format-schedule.pipe';

describe('FormatSchedulePipe', () => {
    let pipe: FormatSchedulePipe;

    beforeEach(() => {
        pipe = new FormatSchedulePipe();
    });

    it('can instantiate FormatSchedulePipe', () => {
        // Then
        expect(pipe).toBeTruthy();
    });

    describe('Methods::', () => {
        describe('|transform|', () => {
            it('should verify on missing schedule returns empty result', () => {
                // Given
                const schedule: string = null;

                // When
                const result = pipe.transform(schedule);

                // Then
                expect(result).toBe('');
            });

            it('should verify on missing schedule returns default value', () => {
                // Given
                const schedule: string = null;
                const defaultResult = 'default001';

                //When
                const result = pipe.transform(schedule, defaultResult);

                // Then
                expect(result).toBe(defaultResult);
            });

            it('should verify will correctly translate cron "5 5 5 2 *"', () => {
                // Given
                const schedule = '5 5 5 2 *';

                // When
                const result = pipe.transform(schedule);

                // Then
                expect(result).toBeDefined();
                expect(result).toContain('At 05:05 AM');
            });

            it('should verify will return parsing error message invalid cron "65 65 65 65 65"', () => {
                // Given
                const schedule = '65 65 65 65 65';

                // When
                const result = pipe.transform(schedule);

                // Then
                expect(result).toBeDefined();
                expect(result).toContain(
                    `Invalid Cron expression "${schedule}"`
                );
            });

            describe('testing minute range', () => {
                it('should verify will correctly translate cron "0 11 10 7 *"', () => {
                    // Given
                    const schedule = '0 11 10 7 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'At 11:00 AM, on day 10 of the month, only in July'
                    );
                });

                it('should verify will correctly translate cron "59 11 10 7 *"', () => {
                    // Given
                    const schedule = '59 11 10 7 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'At 11:59 AM, on day 10 of the month, only in July'
                    );
                });

                it('should verify will return parsing error message invalid cron "60 11 10 7 *"', () => {
                    // Given
                    const schedule = '60 12 10 7 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        `Invalid Cron expression "${schedule}"`
                    );
                });
            });

            describe('testing hour range', () => {
                it('should verify will correctly translate cron "30 0 10 7 *"', () => {
                    // Given
                    const schedule = '30 0 10 7 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'At 12:30 AM, on day 10 of the month, only in July'
                    );
                });

                it('should verify will correctly translate cron "30 23 10 7 *"', () => {
                    // Given
                    const schedule = '30 23 10 7 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'At 11:30 PM, on day 10 of the month, only in July'
                    );
                });

                it('should verify will return parsing error message invalid cron "30 24 10 7 *"', () => {
                    // Given
                    const schedule = '30 24 10 7 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        `Invalid Cron expression "${schedule}"`
                    );
                });
            });

            describe('testing day range', () => {
                it('should verify will correctly translate cron "30 11 1 7 *"', () => {
                    // Given
                    const schedule = '30 11 1 7 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'At 11:30 AM, on day 1 of the month, only in July'
                    );
                });

                it('should verify will correctly translate cron "30 11 31 7 *"', () => {
                    // Given
                    const schedule = '30 11 31 7 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'At 11:30 AM, on day 31 of the month, only in July'
                    );
                });

                it('should verify will return parsing error message invalid cron "30 11 0 7 *"', () => {
                    // Given
                    const schedule = '30 11 0 7 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        `Invalid Cron expression "${schedule}"`
                    );
                });

                it('should verify will return parsing error message invalid cron "30 11 32 7 *"', () => {
                    // Given
                    const schedule = '30 11 32 7 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        `Invalid Cron expression "${schedule}"`
                    );
                });
            });

            describe('testing month range', () => {
                it('should verify will correctly translate cron "30 11 10 1 *"', () => {
                    // Given
                    const schedule = '30 11 10 1 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'At 11:30 AM, on day 10 of the month, only in January'
                    );
                });

                it('should verify will correctly translate cron "30 11 10 12 *"', () => {
                    // Given
                    const schedule = '30 11 10 12 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'At 11:30 AM, on day 10 of the month, only in December'
                    );
                });

                it('should verify will return parsing error message invalid cron "30 11 10 0 *"', () => {
                    // Given
                    const schedule = '30 11 10 0 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        `Invalid Cron expression "${schedule}"`
                    );
                });

                it('should verify will return parsing error message invalid cron "30 11 10 13 *"', () => {
                    // Given
                    const schedule = '30 11 10 13 *';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        `Invalid Cron expression "${schedule}"`
                    );
                });
            });

            describe('testing day of week range', () => {
                it('should verify will correctly translate cron "30 11 10 7 0"', () => {
                    // Given
                    const schedule = '30 11 10 7 0';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'At 11:30 AM, on day 10 of the month, and on Sunday, only in July'
                    );
                });

                it('should verify will correctly translate cron "30 11 10 7 6"', () => {
                    // Given
                    const schedule = '30 11 10 7 6';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'At 11:30 AM, on day 10 of the month, and on Saturday, only in July'
                    );
                });

                it('should verify will correctly translate cron "30 11 10 7 7"', () => {
                    // Given
                    const schedule = '30 11 10 7 7';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'At 11:30 AM, on day 10 of the month, and on Sunday, only in July'
                    );
                });

                it('should verify will return parsing error message invalid cron "30 11 10 7 8"', () => {
                    // Given
                    const schedule = '30 11 10 7 8';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        `Invalid Cron expression "${schedule}"`
                    );
                });
            });

            describe('testing non-standard cron expressions', () => {
                it('should verify will correctly translate cron "@hourly"', () => {
                    // Given
                    const schedule = '@hourly';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'Run once an hour at the beginning of the hour'
                    );
                });

                it('should verify will correctly translate cron "@daily" and "@midnight"', () => {
                    // Given
                    const schedule1 = '@daily';
                    const schedule2 = '@midnight';

                    // When
                    const result1 = pipe.transform(schedule1);
                    const result2 = pipe.transform(schedule2);

                    // Then
                    expect(result1).toBeDefined();
                    expect(result1).toContain('Run once a day at midnight');
                    expect(result2).toBeDefined();
                    expect(result2).toContain('Run once a day at midnight');
                });

                it('should verify will correctly translate cron "@weekly"', () => {
                    // Given
                    const schedule = '@weekly';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'Run once a week at midnight on Sunday morning'
                    );
                });

                it('should verify will correctly translate cron "@monthly"', () => {
                    // Given
                    const schedule = '@monthly';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        'Run once a month at midnight of the first day of the month'
                    );
                });

                it('should verify will correctly translate cron "@yearly" and "@annually"', () => {
                    // Given
                    const schedule1 = '@yearly';
                    const schedule2 = '@annually';

                    // When
                    const result1 = pipe.transform(schedule1);
                    const result2 = pipe.transform(schedule2);

                    // Then
                    expect(result1).toBeDefined();
                    expect(result1).toContain(
                        'Run once a year at midnight of 1 January'
                    );
                    expect(result2).toBeDefined();
                    expect(result2).toContain(
                        'Run once a year at midnight of 1 January'
                    );
                });

                it('should verify will return parsing error message invalid cron "yearly"', () => {
                    // Given
                    const schedule = 'yearly';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        `Invalid Cron expression "${schedule}"`
                    );
                });

                it('should verify will return parsing error message invalid cron "some random text"', () => {
                    // Given
                    const schedule = 'some random text';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        `Invalid Cron expression "${schedule}"`
                    );
                });

                it('should verify will return parsing error message invalid cron "some random text"', () => {
                    // Given
                    const schedule = 'some random text';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        `Invalid Cron expression "${schedule}"`
                    );
                });

                it('should verify will return parsing error message invalid cron "yearly"', () => {
                    // Given
                    const schedule = 'yearly';

                    // When
                    const result = pipe.transform(schedule);

                    // Then
                    expect(result).toBeDefined();
                    expect(result).toContain(
                        `Invalid Cron expression "${schedule}"`
                    );
                });
            });
        });
    });
});
