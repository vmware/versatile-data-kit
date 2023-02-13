/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'parseEpoch'
})
export class ParseEpochPipe implements PipeTransform {
    /**
     * ** Transform to Epoch time.
     *
     *      - This method should be equal to instance method.
     *      - Methods: {@link ParseEpochPipe.transform}
     */
    static transform(nextRunEpochSeconds: number): Date {
        if (nextRunEpochSeconds < 0) {
            return null;
        }

        return new Date(nextRunEpochSeconds * 1000);
    }

    /**
     * @inheritDoc
     *
     *      - This method should be equal to instance method.
     *      - Methods: {@link ParseEpochPipe.transform}
     */
    transform(nextRunEpochSeconds: number): Date {
        return ParseEpochPipe.transform(nextRunEpochSeconds);
    }
}
