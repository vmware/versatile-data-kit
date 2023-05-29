/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';
import { ParseNextRunPipe } from './parse-next-run.pipe';

describe('ParseNextRunPipe', () => {
    let pipe: ParseNextRunPipe;

    beforeEach(() => {
        TestBed.configureTestingModule({ providers: [ParseNextRunPipe] });
        pipe = TestBed.inject(ParseNextRunPipe);
    });

    it('can instantiate ParseNextRunPipe', () => {
        expect(pipe).toBeTruthy();
    });

    describe('Methods::', () => {
        describe('|transform|', () => {
            it('transforms invalid cron to null date', () => {
                const cron: string = null;
                const nextExecution = 1;
                expect(pipe.transform(cron, nextExecution)).toBe(null);
            });

            it('transforms invalid nextExecution to valid date', () => {
                const cron = '* * * * *';
                const nextExecution: number = null;
                expect(pipe.transform(cron, nextExecution)).toBeDefined();
            });

            it('transforms missing nextExecution to valid date', () => {
                const cron = '* * * * *';
                expect(pipe.transform(cron)).toBeDefined();
            });

            it('transforms valid cron to valid date', () => {
                const cron = '5 5 5 2 *';
                const result = pipe.transform(cron);
                expect(result).toBeDefined();
                expect(result.getMonth()).toBe(1); // 1 means Feb
            });

            it(`should verify will return next first run for cron "0 12 * * *" to DateTime in UTC`, (done) => {
                // Given
                const cron = '0 12 * * *';
                const expected = new Date();
                let useTimeout = false;

                if (expected.getUTCHours() === 11 && expected.getUTCMinutes() === 59 && expected.getUTCSeconds() === 59) {
                    useTimeout = true;
                    expected.setUTCDate(expected.getUTCDate() + 1);
                } else if (expected.getUTCHours() >= 12) {
                    expected.setUTCDate(expected.getUTCDate() + 1);
                }

                const y = expected.getUTCFullYear();
                const _m: number = expected.getUTCMonth() + 1;
                const _d: number = expected.getUTCDate();

                let m = `${_m}`;
                let d = `${_d}`;

                if (_m < 10) {
                    m = `0${_m}`;
                }

                if (_d < 10) {
                    d = `0${_d}`;
                }

                if (useTimeout) {
                    setTimeout(() => {
                        // When
                        const date = pipe.transform(cron, 1);

                        // Then
                        console.log(date.toISOString());
                        expect(date.toISOString()).toEqual(`${y}-${m}-${d}T12:00:00.000Z`);

                        done();
                    });
                } else {
                    // When
                    const date = pipe.transform(cron, 1);

                    // Then
                    console.log(date.toISOString());
                    expect(date.toISOString()).toEqual(`${y}-${m}-${d}T12:00:00.000Z`);

                    done();
                }
            }, 5000);

            it(`should verify will return next second run for cron "45 0/12 * * *" to DateTime in UTC`, (done) => {
                // Given
                const cron = '45 0/12 * * *';
                const expected = new Date();
                let useTimeout = false;
                let lunchTime = false;

                let hh: string;
                let mm: string;

                if (expected.getUTCHours() === 12 && expected.getUTCMinutes() === 44 && expected.getUTCSeconds() === 59) {
                    lunchTime = true;
                    useTimeout = true;
                    expected.setUTCDate(expected.getUTCDate() + 1);
                } else if (expected.getUTCHours() === 0 && expected.getUTCMinutes() === 44 && expected.getUTCSeconds() === 59) {
                    useTimeout = true;
                    expected.setUTCDate(expected.getUTCDate() + 1);
                } else if ((expected.getUTCHours() >= 12 && expected.getUTCMinutes() >= 45) || expected.getUTCHours() >= 13) {
                    lunchTime = true;
                    expected.setUTCDate(expected.getUTCDate() + 1);
                } else if (expected.getUTCHours() === 0 && expected.getUTCMinutes() < 45) {
                    lunchTime = true;
                } else {
                    expected.setUTCDate(expected.getUTCDate() + 1);
                }

                const y = expected.getUTCFullYear();
                const _m: number = expected.getUTCMonth() + 1;
                const _d: number = expected.getUTCDate();

                let m = `${_m}`;
                let d = `${_d}`;

                if (_m < 10) {
                    m = `0${m}`;
                }

                if (_d < 10) {
                    d = `0${d}`;
                }

                if (lunchTime) {
                    hh = '12';
                    mm = '45';
                } else {
                    hh = '00';
                    mm = '45';
                }

                if (useTimeout) {
                    setTimeout(() => {
                        // When
                        const date = pipe.transform(cron, 2);

                        // Then
                        console.log(date.toISOString());
                        expect(date.toISOString()).toEqual(`${y}-${m}-${d}T${hh}:${mm}:00.000Z`);

                        done();
                    }, 2000);
                } else {
                    // When
                    const date = pipe.transform(cron, 2);

                    // Then
                    console.log(date.toISOString());
                    expect(date.toISOString()).toEqual(`${y}-${m}-${d}T${hh}:${mm}:00.000Z`);

                    done();
                }
            }, 10000);
        });
    });
});
