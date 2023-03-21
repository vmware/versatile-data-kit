/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Comparable, Predicate } from '../../interfaces';

import { PredicatesComparable } from '../comparable';

export abstract class CompoundPredicate implements Predicate<PredicatesComparable, Comparable> {
    /**
     * @inheritDoc
     */
    readonly comparable: PredicatesComparable;

    /**
     * ** Constructor.
     */
    constructor(comparable: PredicatesComparable);
    constructor(...predicates: Predicate[]);
    constructor(...values: Predicate[] | [PredicatesComparable]) {
        if (values.length === 1) {
            if (values[0] instanceof PredicatesComparable) {
                this.comparable = values[0];
            } else {
                this.comparable = PredicatesComparable.of(values[0]);
            }
        } else {
            this.comparable = PredicatesComparable.of(...(values as Predicate[]));
        }
    }

    /**
     * ** Factory method.
     */
    static of(..._args: unknown[]): CompoundPredicate {
        throw new Error('Method have to be overridden in Subclasses.');
    }

    /**
     * @inheritDoc
     */
    abstract evaluate(value: Comparable): boolean;
}
