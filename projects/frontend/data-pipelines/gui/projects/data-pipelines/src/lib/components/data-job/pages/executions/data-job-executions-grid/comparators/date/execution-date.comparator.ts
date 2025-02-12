/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { get } from 'lodash';

import { Comparator } from '@versatiledatakit/shared';

import { GridDataJobExecution } from '../../../model/data-job-execution';

export class ExecutionDateComparator implements Comparator<GridDataJobExecution> {
    /**
     * ** Property path to value from GridDataJobExecution object.
     */
    public readonly property: keyof GridDataJobExecution;

    /**
     * ** Sort direction.
     */
    public readonly direction: 'ASC' | 'DESC';

    /**
     * ** Constructor.
     */
    constructor(property: keyof GridDataJobExecution, direction: 'ASC' | 'DESC') {
        this.property = property;
        this.direction = direction;
    }

    /**
     * @inheritDoc
     */
    compare(exec1: GridDataJobExecution, exec2: GridDataJobExecution): number {
        const value1 = get<GridDataJobExecution, keyof GridDataJobExecution>(exec1, this.property) as string;
        const value2 = get<GridDataJobExecution, keyof GridDataJobExecution>(exec2, this.property) as string;

        const date1 = value1 ? Date.parse(value1) : Date.now();
        const date2 = value2 ? Date.parse(value2) : Date.now();

        return this.direction === 'ASC' ? date1 - date2 : date2 - date1;
    }
}
