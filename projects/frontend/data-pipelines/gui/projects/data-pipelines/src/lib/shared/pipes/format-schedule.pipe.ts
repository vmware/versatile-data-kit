/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable no-underscore-dangle */

import { Pipe, PipeTransform } from '@angular/core';

import cronstrue from 'cronstrue';

import { CollectionsUtil } from '@versatiledatakit/shared';

@Pipe({
    name: 'formatSchedule',
})
export class FormatSchedulePipe implements PipeTransform {
    private static _fallbackTransformNonStandardCron(cron: string): string {
        const match = `${cron}`
            .trim()
            .match(
                /^@hourly|@daily|@midnight|@weekly|@monthly|@yearly|@annually$/,
            );

        if (CollectionsUtil.isNil(match)) {
            throw new Error('Cron expression cannot be null or undefined.');
        }

        switch (match.input) {
            case '@hourly':
                return 'Run once an hour at the beginning of the hour';
            case '@daily':
            case '@midnight':
                return 'Run once a day at midnight';
            case '@weekly':
                return 'Run once a week at midnight on Sunday morning';
            case '@monthly':
                return 'Run once a month at midnight of the first day of the month';
            case '@yearly':
            case '@annually':
                return 'Run once a year at midnight of 1 January';
            default:
                throw new Error(
                    'Cron expression is NOT nonstandard predefined scheduling definition.',
                );
        }
    }

    /**
     * @inheritDoc
     *
     *      - Cron schedule default format from kubernetes https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/
     *      - Time in UTC
     */
    transform(cronSchedule: string, defaultResult?: string): string {
        try {
            const defaultValue = defaultResult ?? '';

            if (!cronSchedule) {
                return defaultValue;
            }

            //TODO : https://github.com/bradymholt/cRonstrue/issues/94
            // cronstrue doesn't support timezones. Need to use another library
            return cronstrue.toString(cronSchedule, {
                monthStartIndexZero: false,
                dayOfWeekStartIndexZero: true,
            });
        } catch (e) {
            try {
                return FormatSchedulePipe._fallbackTransformNonStandardCron(
                    cronSchedule,
                );
            } catch (_e) {
                console.error(
                    `Parsing error. Cron expression "${cronSchedule}"`,
                );

                return `Invalid Cron expression "${cronSchedule}"`;
            }
        }
    }
}
