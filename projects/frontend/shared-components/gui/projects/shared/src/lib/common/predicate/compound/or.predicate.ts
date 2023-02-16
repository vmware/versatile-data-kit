

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Comparable, Predicate } from '../../interfaces';

import { PredicatesComparable } from '../comparable';

import { CompoundPredicate } from './base-compound.predicate';

export class Or extends CompoundPredicate {

    /**
     * ** Factory method.
     */
    static override of(comparable: PredicatesComparable): Or;
    static override of(...predicates: Predicate[]): Or;
    static override of(...values: Predicate[] | [PredicatesComparable]): Or {
        if (values[0] instanceof PredicatesComparable) {
            return new Or(values[0]);
        } else {
            return new Or(...values as Predicate[]);
        }
    }

    /**
     * @inheritDoc
     */
    evaluate(comparable: Comparable): boolean {
        return this.comparable.like(comparable);
    }
}
