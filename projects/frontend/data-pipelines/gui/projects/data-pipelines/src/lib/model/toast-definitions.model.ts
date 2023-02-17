/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { VmwToastType } from '@vdk/shared';

import { Toast } from '@vdk/shared';

export class ToastDefinitions {
    static successfullyRanJob(jobName: string): Toast {
        return {
            type: VmwToastType.INFO,
            title: `Data job Queued for execution`,
            description: `Data job "${ jobName }" successfully queued for execution.`
        };
    }
}
