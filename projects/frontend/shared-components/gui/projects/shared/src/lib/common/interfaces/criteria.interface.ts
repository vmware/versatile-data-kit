/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * ** Interface for filtering data according some criteria.
 */
export interface Criteria<T = unknown> {
    /**
     * ** Creates new filtered Array of elements that meets the criteria.
     *
     *      - Does not modify the original Array.
     */
    meetCriteria(elements: T[]): T[];
}
