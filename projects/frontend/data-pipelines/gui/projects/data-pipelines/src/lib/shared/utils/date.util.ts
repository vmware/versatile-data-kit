/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataJobExecution } from '../../model';

export class DateUtil {
    static compareDatesAsc(
        left: DataJobExecution,
        right: DataJobExecution,
    ): number {
        const leftStartTime = left.startTime ?? 0;
        const rightStartTime = right.endTime ?? 0;

        return (
            new Date(leftStartTime).getTime() -
            new Date(rightStartTime).getTime()
        );
    }

    static normalizeToUTC(dateISO: string): Date {
        return new Date(dateISO.replace(/Z$/, ''));
    }
}
