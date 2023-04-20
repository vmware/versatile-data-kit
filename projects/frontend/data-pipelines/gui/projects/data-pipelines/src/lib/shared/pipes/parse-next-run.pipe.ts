/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Pipe, PipeTransform } from '@angular/core';

import * as parser from 'cron-parser';

@Pipe({
    name: 'parseNextRun'
})
export class ParseNextRunPipe implements PipeTransform {
    /**
     * @inheritDoc
     */
    transform(cron: string, nextExecution?: number): Date {
        if (!cron) {
            return null;
        }

        if (!nextExecution) {
            nextExecution = 1;
        }

        let result: Date;
        try {
            const parsedDate = parser.parseExpression(cron, { utc: true });
            for (let i = 0; i < nextExecution; i++) {
                result = parsedDate.next().toDate();
            }
        } catch (e) {
            result = null;
            console.error('Error parsing next run', e);
        }
        return result;
    }
}
