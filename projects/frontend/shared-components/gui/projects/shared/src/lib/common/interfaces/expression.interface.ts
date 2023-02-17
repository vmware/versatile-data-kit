

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Comparable } from './comparable.interface';
import { Predicate } from './predicate.interface';

/**
 * ** Interface for Expression.
 *
 *
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
