/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * ** Interface for Comparison data.
 */
export interface Comparable<T = unknown> {
    /**
     * ** Value stored in Comparable for Comparison.
     */
    readonly value: T;

    /**
     * ** Compares stored data with the provided one.
     *
     *   -1 if the stored value is less than the provided value.
     *   0 if both values are equal.
     *   1 if stored value is bigger than the provided value.
     */
    compare(comparable: Comparable): number;

    /**
     * ** Verify if stored value is null or undefined and returns true.
     */
    isNil(): boolean;

    /**
     * ** Verify if stored value is not null and not undefined.
     */
    notNil(): boolean;

    /**
     * ** Compare if stored value is similar to provided value.
     */
    like(comparable: Comparable): boolean;

    /**
     * ** Verify if stored value is equals with provided value.
     */
    equal(comparable: Comparable): boolean;

    /**
     * ** Verify if stored value is different than provided value.
     */
    notEqual(comparable: Comparable): boolean;

    /**
     * ** Verify if stored value is less than provided value.
     */
    lessThan(comparable: Comparable): boolean;

    /**
     * ** Verify if stored value is less or equal than provided value.
     */
    lessThanInclusive(comparable: Comparable): boolean;

    /**
     * ** Verify if stored value is greater than provided value.
     */
    greaterThan(comparable: Comparable): boolean;

    /**
     * ** Verify if stored value is greater or equal than provided value.
     */
    greaterThanInclusive(comparable: Comparable): boolean;
}
