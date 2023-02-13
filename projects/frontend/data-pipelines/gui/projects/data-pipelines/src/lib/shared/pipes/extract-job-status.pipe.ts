/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Pipe, PipeTransform } from '@angular/core';

import { DataJobStatus, StatusDetails } from '../../model';

@Pipe({
    name: 'extractJobStatus',
    pure: false
})
export class ExtractJobStatusPipe implements PipeTransform {
    /**
     * ** Extract Job Status from Details.
     *
     *      - This method should be equal to instance method.
     *      - Methods: {@link ExtractJobStatusPipe.transform}
     */
    static transform(jobDeployments: StatusDetails[]): DataJobStatus {
        if (!jobDeployments?.length) {
            return DataJobStatus.NOT_DEPLOYED;
        }

        if (jobDeployments[jobDeployments.length - 1].enabled) {
            return DataJobStatus.ENABLED;
        }

        return DataJobStatus.DISABLED;
    }

    /**
     * @inheritDoc
     *
     *      - This method should be equal to instance method.
     *      - Methods: {@link ExtractJobStatusPipe.transform}
     */
    transform(jobDeployments: StatusDetails[]): DataJobStatus {
        return ExtractJobStatusPipe.transform(jobDeployments);
    }
}
