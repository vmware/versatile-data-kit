/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { BaseDataJobDeployment, DataJobExecutionStatus } from './data-job-base.model';

export interface DataJobDeployment extends BaseDataJobDeployment {
    lastDeployedDate?: string;
    lastDeployedBy?: string;
    lastExecutionStatus?: DataJobExecutionStatus;
    lastExecutionDuration?: number;
    lastExecutionTime?: string;
    successfulExecutions?: number;
    failedExecutions?: number;
}
