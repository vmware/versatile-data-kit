

/* eslint-disable @typescript-eslint/no-explicit-any */

import { Comparable } from '../../interfaces';

import { CollectionsUtil } from '../../../utils';

/**
 * ** Comparable.
 *
 * @author gorankokin
 */
export class ComparableImpl<T = unknown> implements Comparable<T> {

    /**
     * @inheritDoc
     */
    public readonly value: T;

    /**
     * ** Constructor.
     */
    constructor(value: T) {
        this.value = value;
    }

    /**
     * ** Factory method.
     */
    static of(value: any): ComparableImpl {
        return new ComparableImpl(value);
    }

    /**
     * @inheritDoc
     */
    compare(comparable: Comparable): number {
        if (comparable instanceof ComparableImpl) {
            const evaluateSecondStatement = () => this.value > comparable.value
                ? 1
                : -1;

            return this.value === comparable.value
                ? 0
                : evaluateSecondStatement();
        } else {
            return -1;
        }
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
        return this.compare(comparable) === 0;
    }

    /**
     * @inheritDoc
     */
    equal(comparable: Comparable): boolean {
        return this.compare(comparable) === 0;
    }

    /**
     * @inheritDoc
     */
    notEqual(comparable: Comparable): boolean {
        return this.compare(comparable) !== 0;
    }

    /**
     * @inheritDoc
     */
    lessThan(comparable: Comparable): boolean {
        return this.compare(comparable) < 0;
    }

    /**
     * @inheritDoc
     */
    lessThanInclusive(comparable: Comparable): boolean {
        return this.compare(comparable) <= 0;
    }

    /**
     * @inheritDoc
     */
    greaterThan(comparable: Comparable): boolean {
        return this.compare(comparable) > 0;
    }

    /**
     * @inheritDoc
     */
    greaterThanInclusive(comparable: Comparable): boolean {
        return this.compare(comparable) >= 0;
    }
}
