/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Comparable } from '../../interfaces';

import { SimplePredicate } from './base-simple.predicate';

/**
 * ** Equal Predicate that accepts Comparable and make equality evaluation.
 *
 *
 */
export class Equal<
	T extends Comparable = Comparable
> extends SimplePredicate<T> {
	/**
	 * ** Constructor.
	 */
	constructor(comparable: T) {
		super(comparable);
	}

	/**
	 * ** Factory method.
	 */
	static override of(comparable: Comparable): Equal {
		return new Equal(comparable);
	}

	/**
	 * @inheritDoc
	 */
	evaluate(comparable: Comparable): boolean {
		return this.comparable.equal(comparable);
	}
}
