/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { Comparable } from './comparable.interface';

/**
 * ** Interface for Predicate Classes.
 */
export interface Predicate<T extends Comparable = Comparable, C extends Comparable = T> {
    /**
     * ** Stored comparable that have to be compared with provided comparable.
     */
    readonly comparable: T;

    /**
     * ** Evaluate Predicate to boolean (true or false).
     */
    evaluate(comparable: C): boolean;
}
