/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Comparable, Predicate } from '../../interfaces';

export abstract class SimplePredicate<T extends Comparable = Comparable>
	implements Predicate<T>
{
	/**
	 * @inheritDoc
	 */
	readonly comparable: T;

	/**
	 * ** Constructor.
	 */
	protected constructor(comparable: T) {
		this.comparable = comparable;
	}

	/**
	 * ** Factory method.
	 */
	static of(..._args: unknown[]): SimplePredicate {
		throw new Error('Method have to be overridden in Subclasses.');
	}

	/**
	 * @inheritDoc
	 */
	abstract evaluate(comparable: T): boolean;
}
