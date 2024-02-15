/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2023-2024 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * ** Comparator interface.
 */
export interface Comparator<T = unknown> {
    /**
     * ** Executes comparison between two values.
     */
    compare(a: T, b: T): -1 | 0 | 1 | number;
}
