/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import * as parser from 'cron-parser';

export class CronUtil {
    static getNextExecutionErrors(cron: string): string {
        if (!cron) {
            return 'No schedule cron configured for this job';
        }
        try {
            parser.parseExpression(cron);
            return null; // parsing successful, reset flag
        } catch (e: unknown) {
            // eslint-disable-next-line @typescript-eslint/restrict-template-expressions
            return `Could not extract next executions from the cron expression: ${ e }`;
        }
    }
}
