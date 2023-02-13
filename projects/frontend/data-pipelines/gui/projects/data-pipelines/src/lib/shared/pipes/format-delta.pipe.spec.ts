/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { DataJobExecution, DataJobExecutionStatus, DataJobExecutionType } from '../../model';

import { FormatDeltaPipe } from './format-delta.pipe';

const TEST_JOBS_EXECUTIONS = {
    id: 'id001',
    jobName: 'name001',
    status: DataJobExecutionStatus.RUNNING,
    startTime: new Date().toISOString(),
    startedBy: 'aUserov',
    type: DataJobExecutionType.SCHEDULED,
    endTime: new Date().toISOString(),
    opId: 'op001',
    message: 'Message 001'
} as DataJobExecution;

describe('FormatDeltaPipe', () => {
    let pipe: FormatDeltaPipe;
    let execution: DataJobExecution;

    beforeEach(() => {
        TestBed.configureTestingModule({ providers: [FormatDeltaPipe] });
        pipe = TestBed.inject(FormatDeltaPipe);
        execution = { ...TEST_JOBS_EXECUTIONS };
    });

    it('can instantiate FormatDeltaPipe', () => {
        expect(pipe).toBeTruthy();
    });

    it('transforms missing startTime to valid value', (): void => {
        execution.startTime = undefined;
        execution.endTime = undefined;
        expect(pipe.transform(execution)).toEqual('');
    });

    it('transforms invalid EndData to valid delta', (): void => {
        execution.startTime = substract(new Date().toISOString(), 1);
        execution.endTime = null;
        expect(pipe.transform(execution)).toBeDefined();
    });

    it('transforms a out of range input to NaN delta', (): void => {
        const currentDate = new Date().toISOString();
        execution.startTime = substract(currentDate, -10);
        execution.endTime = currentDate;
        expect(pipe.transform(execution)).toBe('N/A');
    });

    it('transforms a seconds range input to valid delta', (): void => {
        const currentDate = new Date().toISOString();
        execution.startTime = substract(currentDate, 10);
        execution.endTime = currentDate;
        expect(pipe.transform(execution)).toBe('10s');
    });

    it('transforms a minutes range input to valid delta', (): void => {
        const currentDate = new Date().toISOString();
        execution.startTime = substract(currentDate, 121);
        execution.endTime = currentDate;
        expect(pipe.transform(execution)).toBe('2m 1s');
    });

    it('transforms an hours range input to valid delta', (): void => {
        const currentDate = new Date().toISOString();
        execution.startTime = substract(currentDate, 7260);
        execution.endTime = currentDate;
        expect(pipe.transform(execution)).toBe('2h 1m');
    });

    it('transforms a days range input to valid delta', (): void => {
        const currentDate = new Date().toISOString();
        execution.startTime = substract(currentDate, 176400);
        execution.endTime = currentDate;
        expect(pipe.transform(execution)).toBe('2d 1h');
    });

    const substract = (date: string, secondsToSubstract: number) => {
        const d = new Date(date);
        const result = d;
        result.setTime(d.getTime() - (1000 * secondsToSubstract));

        return result.toISOString();
    };
});
