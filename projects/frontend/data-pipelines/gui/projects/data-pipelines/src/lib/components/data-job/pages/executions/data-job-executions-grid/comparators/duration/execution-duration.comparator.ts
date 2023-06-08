/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Comparator } from '@versatiledatakit/shared';

import { GridDataJobExecution } from '../../../model/data-job-execution';

export class ExecutionDurationComparator implements Comparator<GridDataJobExecution> {
    public readonly direction: 'ASC' | 'DESC';

    /**
     * ** Constructor.
     */
    constructor(direction: 'ASC' | 'DESC') {
        this.direction = direction;
    }

    /**
     * @inheritDoc
     */
    compare(exec1: GridDataJobExecution, exec2: GridDataJobExecution): number {
        const aDuration = Date.parse(exec1.endTime) - Date.parse(exec1.startTime);
        const bDuration = Date.parse(exec2.endTime) - Date.parse(exec2.startTime);

        return this.direction === 'ASC' ? aDuration - bDuration : bDuration - aDuration;
    }
}
