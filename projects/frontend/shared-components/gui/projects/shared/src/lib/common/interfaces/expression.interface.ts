/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { Comparable } from './comparable.interface';
import { Predicate } from './predicate.interface';

/**
 * ** Interface for Expression.
 */
export interface Expression<T extends Predicate = Predicate> {
    /**
     * ** Predicates Array.
     */
    readonly predicates: T[];

    /**
     * ** Evaluate Expression to boolean (true or false).
     */
    evaluate(comparable?: Comparable): boolean;
}
