/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Pipe, PipeTransform } from '@angular/core';

import { CollectionsUtil } from '@vdk/shared';

import { DataJobExecution } from '../../model';

/**
 * Format Delta Pipe formats the delta of the execution start and end Time.
 * The format is dynamic and contains generaly the last two leading fragment of the duration.
 *
 * For example:
 *
 *   1: If the duration is less than 1 min, the format is `${seconds}s`
 *
 *   2: If the duration is between 1 min and 59 mins, the format is `${minutes}m ${seconds}s`
 *
 *   3: If the duration is between 1 hour and 1 day, the format is `${hours}h ${minutes}m`
 *
 *   4: If the duration is more than 1 day, the format is `${days}d ${hours}h`
 */
@Pipe({
    name: 'formatDelta'
})
export class FormatDeltaPipe implements PipeTransform {
    static formatDelta(delta: number): string {
        if (delta < 0) {
            return 'N/A';
        } else if (delta < 60) {
            return `${ Math.ceil(delta) }s`;
        } else if (delta < 3600) {
            const minute = Math.floor((delta / (60) % 60));
            const seconds = Math.floor(delta % 60);

            return `${ minute }m ${ seconds }s`;
        } else if (delta < 86400) {
            const hours = Math.floor((delta / (60 * 60) % 24));
            const minutes = Math.floor((delta / (60) % 60));

            return `${ hours }h ${ minutes }m`;
        } else {
            const days = Math.floor((delta / (60 * 60 * 24)));
            const hours = Math.floor((delta / (60 * 60) % 24));

            return `${ days }d ${ hours }h`;
        }
    }

    /**
     * @inheritDoc
     */
    transform(execution: DataJobExecution): string {
        if (CollectionsUtil.isNil(execution.startTime)) {
            return '';
        }

        const delta = (FormatDeltaPipe._getEndTime(execution) - FormatDeltaPipe._getStartTime(execution)) / 1000;

        return FormatDeltaPipe.formatDelta(delta);
    }

    // eslint-disable-next-line @typescript-eslint/member-ordering
    private static _getStartTime(execution: DataJobExecution): number {
        if (CollectionsUtil.isDefined(execution.startTime)) {
            return new Date(execution.startTime).getTime();
        }

        return Date.now();
    }

    // eslint-disable-next-line @typescript-eslint/member-ordering
    private static _getEndTime(execution: DataJobExecution): number {
        if (CollectionsUtil.isDefined(execution.endTime)) {
            return new Date(execution.endTime).getTime();
        }

        return Date.now();
    }
}
