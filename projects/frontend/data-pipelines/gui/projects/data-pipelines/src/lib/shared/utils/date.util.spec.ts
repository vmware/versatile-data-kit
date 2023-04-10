/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataJobExecution, DataJobExecutionStatus, DataJobExecutionType } from '../../model';

import { DateUtil } from './date.util';

const LESSER_DATE_JOBS_EXECUTION: DataJobExecution = {
    id: 'oneId',
    startTime: new Date(1).toISOString(),
    jobName: 'oneJob',
    status: DataJobExecutionStatus.SUBMITTED,
    startedBy: '',
    type: DataJobExecutionType.MANUAL,
    endTime: new Date(1).toISOString(),
    opId: 'oneOp',
    message: 'oneMessage',
    logsUrl: 'https::/logs.com'
};

const GREATER_DATE_JOBS_EXECUTION: DataJobExecution = {
    id: 'twoId',
    startTime: new Date(2).toISOString(),
    jobName: 'twoJob',
    status: DataJobExecutionStatus.SUBMITTED,
    startedBy: '',
    type: DataJobExecutionType.MANUAL,
    endTime: new Date(2).toISOString(),
    opId: 'twoOp',
    message: 'twoMessage',
    logsUrl: 'https::/logs.com'
};

describe('DateUtil', () => {
    it('Compare Dates Asc for equal left and right', () => {
        expect(DateUtil.compareDatesAsc(LESSER_DATE_JOBS_EXECUTION, LESSER_DATE_JOBS_EXECUTION)).toEqual(0);
    });

    it('Compare Dates Asc for greater left', () => {
        expect(DateUtil.compareDatesAsc(GREATER_DATE_JOBS_EXECUTION, LESSER_DATE_JOBS_EXECUTION)).toBeGreaterThan(0);
    });

    it('Compare Dates Asc for greater right', () => {
        expect(DateUtil.compareDatesAsc(LESSER_DATE_JOBS_EXECUTION, GREATER_DATE_JOBS_EXECUTION)).toBeLessThan(0);
    });

    it('GetDateInUTC', () => {
        expect(DateUtil.normalizeToUTC('2021-12-10T10:12:12Z').getHours()).toEqual(10);
    });
});
