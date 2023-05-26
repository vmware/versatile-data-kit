/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil, Criteria } from '@versatiledatakit/shared';

import { DataJobExecutionType } from '../../../../../../../model';

import { GridDataJobExecution } from '../../../model';

/**
 * ** Executions Type filter criteria.
 */
export class ExecutionsTypeCriteria implements Criteria<GridDataJobExecution> {
    private readonly _dataJobExecutionTypes: DataJobExecutionType[];

    /**
     * ** Constructor.
     */
    constructor(dataJobExecutionTypesSerialized: string) {
        this._dataJobExecutionTypes = ExecutionsTypeCriteria._deserializeExecutionTypes(dataJobExecutionTypesSerialized);
    }

    /**
     * @inheritDoc
     */
    meetCriteria(executions: GridDataJobExecution[]): GridDataJobExecution[] {
        return [...(executions ?? [])].filter((execution) => {
            const type = execution.type;

            if (this._dataJobExecutionTypes.length === 0) {
                return true;
            }

            return this._dataJobExecutionTypes.includes(type);
        });
    }

    private static _deserializeExecutionTypes(dataJobExecutionTypesSerialized: string): DataJobExecutionType[] {
        try {
            if (!CollectionsUtil.isStringWithContent(dataJobExecutionTypesSerialized)) {
                return [];
            }

            return dataJobExecutionTypesSerialized.toUpperCase().split(',') as DataJobExecutionType[];
        } catch (e) {
            console.error(`ExecutionsTypeCriteria: failed to deserialize Data Job Execution Types.`);

            return [];
        }
    }
}
