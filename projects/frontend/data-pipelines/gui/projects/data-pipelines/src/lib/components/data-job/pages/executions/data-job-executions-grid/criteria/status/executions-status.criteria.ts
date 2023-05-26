/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil, Criteria } from '@versatiledatakit/shared';

import { DataJobExecutionStatus } from '../../../../../../../model';

import { GridDataJobExecution } from '../../../model';

/**
 * ** Executions Status filter criteria.
 */
export class ExecutionsStatusCriteria implements Criteria<GridDataJobExecution> {
    private readonly _dataJobExecutionStatuses: DataJobExecutionStatus[];

    /**
     * ** Constructor.
     */
    constructor(dataJobExecutionStatusesSerialized: string) {
        this._dataJobExecutionStatuses = ExecutionsStatusCriteria._deserializeExecutionStatuses(dataJobExecutionStatusesSerialized);
    }

    /**
     * @inheritDoc
     */
    meetCriteria(executions: GridDataJobExecution[]): GridDataJobExecution[] {
        return [...(executions ?? [])].filter((execution) => {
            const status = execution.status;

            if (this._dataJobExecutionStatuses.length === 0) {
                return true;
            }

            return this._dataJobExecutionStatuses.includes(status);
        });
    }

    private static _deserializeExecutionStatuses(dataJobExecutionStatusesSerialized: string): DataJobExecutionStatus[] {
        try {
            if (!CollectionsUtil.isStringWithContent(dataJobExecutionStatusesSerialized)) {
                return [];
            }

            return dataJobExecutionStatusesSerialized.toUpperCase().split(',') as DataJobExecutionStatus[];
        } catch (e) {
            console.error(`ExecutionsStatusCriteria: failed to deserialize Data Job Execution Statuses.`);

            return [];
        }
    }
}
