/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Inject, LOCALE_ID, Pipe, PipeTransform } from '@angular/core';
import { PercentPipe } from '@angular/common';

import { CollectionsUtil } from '@vdk/shared';

import { DataJobDeployment } from '../../model';

@Pipe({
    name: 'executionSuccessRate'
})
export class ExecutionSuccessRatePipe implements PipeTransform {
    private readonly _percentPipe: PercentPipe;

    /**
     * ** Constructor.
     */
    constructor(@Inject(LOCALE_ID) readonly localeId: string) {
        this._percentPipe = new PercentPipe(localeId);
    }

    /**
     * @inheritDoc
     */
    transform(deployments: DataJobDeployment[]): string {
        let result = '';

        if (CollectionsUtil.isArrayEmpty(deployments)) {
            return result;
        }

        const firstDeployment = deployments[0];
        const allExecutions = firstDeployment.successfulExecutions + firstDeployment.failedExecutions;

        if (allExecutions === 0) {
            return result;
        }

        result += this._percentPipe.transform(firstDeployment.successfulExecutions / allExecutions, '1.2-2');

        if (firstDeployment.failedExecutions > 0) {
            result += ` (${ firstDeployment.failedExecutions } failed)`;
        }

        return result;
    }
}
