/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Comparable, Predicate } from '../../interfaces';

import { PredicatesComparable } from '../comparable';

import { CompoundPredicate } from './base-compound.predicate';

export class And extends CompoundPredicate {
    /**
     * ** Factory method.
     */
    static override of(comparable: PredicatesComparable): And;
    static override of(...predicates: Predicate[]): And;
    static override of(...values: Predicate[] | [PredicatesComparable]): And {
        if (values[0] instanceof PredicatesComparable) {
            return new And(values[0]);
        } else {
            return new And(...(values as Predicate[]));
        }
    }

    /**
     * @inheritDoc
     */
    evaluate(comparable: Comparable): boolean {
        return this.comparable.equal(comparable);
    }
}
