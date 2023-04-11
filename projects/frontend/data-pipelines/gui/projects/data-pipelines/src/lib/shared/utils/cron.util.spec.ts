/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CronUtil } from './cron.util';

describe('DateUtil', () => {
    it('expect null argument to return null result', () => {
        expect(CronUtil.getNextExecutionErrors(null)).toBe('No schedule cron configured for this job');
    });

    it('expect invalid argument to return error text', () => {
        expect(CronUtil.getNextExecutionErrors('* * * * * * *')).toContain('');
    });

    it('expect valid argument to return null', () => {
        expect(CronUtil.getNextExecutionErrors('5 5 5 2 *')).toEqual(null);
    });
});
