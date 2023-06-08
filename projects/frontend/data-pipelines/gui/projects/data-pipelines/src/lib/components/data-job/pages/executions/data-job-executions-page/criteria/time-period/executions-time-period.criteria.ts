/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil, Criteria } from '@versatiledatakit/shared';

import { GridDataJobExecution } from '../../../model';

/**
 * ** Executions Time Period filter criteria.
 */
export class ExecutionsTimePeriodCriteria implements Criteria<GridDataJobExecution> {
    private readonly _fromDateTime: Date;
    private readonly _toDateTime: Date;

    /**
     * ** Constructor.
     */
    constructor(fromDateTime: Date, toDateTime: Date) {
        this._fromDateTime = fromDateTime;
        this._toDateTime = toDateTime;
    }

    /**
     * @inheritDoc
     */
    meetCriteria(executions: GridDataJobExecution[]): GridDataJobExecution[] {
        return [...(executions ?? [])].filter((execution) => {
            if (CollectionsUtil.isNil(this._fromDateTime) || CollectionsUtil.isNil(this._toDateTime)) {
                return true;
            }

            if (!CollectionsUtil.isString(execution.startTime)) {
                return false;
            }

            const startTime = new Date(execution.startTime).getTime();

            return this._fromDateTime.getTime() <= startTime && startTime <= this._toDateTime.getTime();
        });
    }
}
