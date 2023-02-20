/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ClrDatagridComparatorInterface } from '@clr/angular';

import { GridDataJobExecution } from '../../model/data-job-execution';

export class DataJobExecutionDurationComparator implements ClrDatagridComparatorInterface<GridDataJobExecution> {
    /**
     * @inheritDoc
     */
    compare(a: GridDataJobExecution, b: GridDataJobExecution) {
        const aDuration = Date.parse(a.endTime) - Date.parse(a.startTime);
        const bDuration = Date.parse(b.endTime) - Date.parse(b.startTime);

        return aDuration - bDuration;
    }
}
