/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

export enum DisplayMode {
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    COMPACT = 'compact',
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    STANDARD = 'standard'
}

export interface GridFilters {
    jobName?: string;
    teamName?: string;
    description?: string;
    deploymentStatus?: string;
    deploymentLastExecutionStatus?: string;
}
