/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { Toast, VmwToastType } from '@versatiledatakit/shared';

export class ToastDefinitions {
    static successfullyRanJob(jobName: string): Toast {
        return {
            type: VmwToastType.INFO,
            title: `Data job Queued for execution`,
            description: `Data job "${jobName}" successfully queued for execution.`
        };
    }
}
