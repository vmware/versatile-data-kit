/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { get } from 'lodash';

import { CollectionsUtil, Criteria } from '@versatiledatakit/shared';

import { GridDataJobExecution } from '../../../model';

/**
 * ** Executions Generic string filter criteria.
 */
export class ExecutionsStringCriteria implements Criteria<GridDataJobExecution> {
    private readonly _property: keyof GridDataJobExecution;
    private readonly _searchValue: GridDataJobExecution[Exclude<keyof GridDataJobExecution, 'deployment'>];

    /**
     * ** Constructor.
     */
    constructor(
        property: keyof GridDataJobExecution,
        searchValue: GridDataJobExecution[Exclude<keyof GridDataJobExecution, 'deployment'>]
    ) {
        this._property = property;
        this._searchValue = searchValue;
    }

    /**
     * @inheritDoc
     */
    meetCriteria(executions: GridDataJobExecution[]): GridDataJobExecution[] {
        return [...(executions ?? [])].filter((execution) => {
            const value = get<GridDataJobExecution, keyof GridDataJobExecution>(execution, this._property);

            if (!CollectionsUtil.isString(this._searchValue)) {
                return true;
            }

            if (!CollectionsUtil.isString(value)) {
                return false;
            }

            return value.toLowerCase().includes(this._searchValue.toLowerCase());
        });
    }
}
