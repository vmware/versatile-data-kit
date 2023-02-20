

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

/**
 * ** Interface for Copy of Object.
 *
 *
 */
export interface Copy<T extends Record<any, any>> {
    /**
     * ** Make shallow copy of current Object.
     *      - Optionally provide partial Object to merge on top of the current one.
     */
    copy(partial?: Partial<T>);
}
