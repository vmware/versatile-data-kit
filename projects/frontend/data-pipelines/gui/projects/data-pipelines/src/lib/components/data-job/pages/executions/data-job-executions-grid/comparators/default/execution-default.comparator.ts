/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { get } from 'lodash';

import { Comparator } from '@versatiledatakit/shared';

import { GridDataJobExecution } from '../../../model/data-job-execution';

/**
 * ** Execution default comparator.
 */
export class ExecutionDefaultComparator implements Comparator<GridDataJobExecution> {
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
    compare(exec1: GridDataJobExecution, exec2: GridDataJobExecution) {
        const value1 = get<GridDataJobExecution, keyof GridDataJobExecution>(exec1, this.property);
        const value2 = get<GridDataJobExecution, keyof GridDataJobExecution>(exec2, this.property);
        const directionModifier = this.direction === 'DESC' ? 1 : -1;

        return (value1 > value2 ? -1 : value2 > value1 ? 1 : 0) * directionModifier;
    }
}
