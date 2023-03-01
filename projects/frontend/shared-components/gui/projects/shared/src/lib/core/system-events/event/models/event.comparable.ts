/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Comparable, ComparableImpl } from '../../../../common';

import { CollectionsUtil } from '../../../../utils';

import { SystemEvent } from './event-helper';

/**
 * @inheritDoc
 *
 *
 */
export class SystemEventComparable extends ComparableImpl<{
	eventId: SystemEvent;
	payload: unknown;
}> {
	/**
	 * ** Constructor.
	 */
	constructor(value: { eventId: string; payload: unknown }) {
		super(value);
	}

	/**
	 * ** Factory method.
	 */
	static override of(value: {
		eventId: string;
		payload: unknown;
	}): SystemEventComparable {
		return new SystemEventComparable(value);
	}

	/**
	 * @inheritDoc
	 */
	override compare(comparable: Comparable): number {
		if (comparable instanceof SystemEventComparable) {
			const evaluateSecondStatement = () =>
				this.value.payload > comparable.value.payload ? 1 : -1;

			return CollectionsUtil.isEqual(
				this.value.payload,
				comparable.value.payload
			)
				? 0
				: evaluateSecondStatement();
		} else {
			return -1;
		}
	}
}
