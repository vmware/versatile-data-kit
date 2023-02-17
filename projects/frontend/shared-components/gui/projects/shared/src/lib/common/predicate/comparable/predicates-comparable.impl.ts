

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil } from '../../../utils';

import { Comparable, Predicate } from '../../interfaces';

export class PredicatesComparable<T extends Predicate[] = Predicate[]> implements Comparable<T> {

    /**
     * @inheritDoc
     */
    public readonly value: T;

    /**
     * ** Constructor.
     */
    constructor(...predicates: T) {
        this.value = predicates ?? [] as T;
    }

    /**
     * ** Factory method.
     */
    static of(...predicates: Predicate[]): PredicatesComparable {
        return new PredicatesComparable(...predicates);
    }

    /**
     * @inheritDoc
     */
    compare(_comparable: Comparable): number {
        console.warn('PredicatesComparable, unsupported comparison.');

        return -1;
    }

    /**
     * @inheritDoc
     */
    isNil(): boolean {
        return CollectionsUtil.isNil(this.value);
    }

    /**
     * @inheritDoc
     */
    notNil(): boolean {
        return CollectionsUtil.isDefined(this.value);
    }

    /**
     * @inheritDoc
     */
    like(comparable: Comparable): boolean {
        return this.value
                   .some((predicate) => predicate.evaluate(comparable));
    }

    /**
     * @inheritDoc
     */
    equal(comparable: Comparable): boolean {
        return this.value
                   .every((predicate) => predicate.evaluate(comparable));
    }

    /**
     * @inheritDoc
     */
    notEqual(comparable: Comparable): boolean {
        return !this.value
                    .every((predicate) => predicate.evaluate(comparable));
    }

    /**
     * @inheritDoc
     */
    lessThan(_comparable: Comparable): boolean {
        return PredicatesComparable._defaultUnsupported();
    }

    /**
     * @inheritDoc
     */
    lessThanInclusive(_comparable: Comparable): boolean {
        return PredicatesComparable._defaultUnsupported();
    }

    /**
     * @inheritDoc
     */
    greaterThan(_comparable: Comparable): boolean {
        return PredicatesComparable._defaultUnsupported();
    }

    /**
     * @inheritDoc
     */
    greaterThanInclusive(_comparable: Comparable): boolean {
        return PredicatesComparable._defaultUnsupported();
    }

    // eslint-disable-next-line @typescript-eslint/member-ordering
    private static _defaultUnsupported(): boolean {
        console.warn('PredicatesComparable, unsupported comparison.');

        return false;
    }
}
