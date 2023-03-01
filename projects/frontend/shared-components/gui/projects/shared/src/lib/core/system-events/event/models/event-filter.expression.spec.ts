/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
	Comparable,
	ComparableImpl,
	Equal,
	Predicate
} from '../../../../common';

import { SystemEventFilterExpression } from './event-filter.expression';

describe('SystemEventFilterExpression', () => {
	let v1: any;
	let v2: any;
	let v3: any;
	let v4: any;

	let c1: Comparable;
	let c2: Comparable;
	let c3: Comparable;
	let c4: Comparable;

	let p1: Predicate;
	let p2: Predicate;
	let p3: Predicate;
	let p4: Predicate;

	beforeEach(() => {
		v1 = 'Taurus';
		v2 = 'Taurus';
		v3 = 'VDK';
		v4 = 'Taurus';

		c1 = ComparableImpl.of(v1);
		c2 = ComparableImpl.of(v2);
		c3 = ComparableImpl.of(v3);
		c4 = ComparableImpl.of(v4);

		p1 = Equal.of(c1);
		p2 = Equal.of(c2);
		p3 = Equal.of(c3);
		p4 = Equal.of(c4);
	});

	it('should verify instance is created', () => {
		// When
		const r = new SystemEventFilterExpression(p1);

		// Then
		expect(r).toBeDefined();
	});

	it('should verify Predicates are correctly assigned', () => {
		// When
		const r = new SystemEventFilterExpression(p1, p2, p3);

		// Then
		expect(r.predicates).toEqual([p1, p2, p3]);
	});

	it('should verify is no Predicates given will create empty Expression', () => {
		// When
		const r1 = SystemEventFilterExpression.of();
		const r2 = new SystemEventFilterExpression();

		// Then
		expect(r1).toBeDefined();
		expect(r1.predicates).toEqual([]);
		expect(r2).toBeDefined();
		expect(r2.predicates).toEqual([]);
	});

	describe('Statics::', () => {
		describe('Methods::()', () => {
			describe('|of|', () => {
				it('should verify factory method will create instance', () => {
					// When
					const r = SystemEventFilterExpression.of(p1, p2, p3, p4);

					// Then
					expect(r).toBeDefined();
					expect(r).toBeInstanceOf(SystemEventFilterExpression);
					expect(r.predicates).toEqual([p1, p2, p3, p4]);
				});
			});
		});
	});

	describe('Methods::()', () => {
		describe('|addPredicate|', () => {
			it('should verify will add new Predicates to existing one', () => {
				// Given
				const e = SystemEventFilterExpression.of(p1);

				// Then 1
				expect(e.predicates).toEqual([p1]);

				// When
				e.addPredicate(p3, p4);
				e.addPredicate(p2);

				// Then 2
				expect(e.predicates).toEqual([p1, p3, p4, p2]);
			});
		});

		describe('|hasPredicates|', () => {
			it('should verify will return true if there is Predicates in Expression, otherwise false', () => {
				// Given
				const e1 = SystemEventFilterExpression.of();
				const e2 = SystemEventFilterExpression.of(p1, p2);

				// When
				const r1 = e1.hasPredicates();
				const r2 = e2.hasPredicates();

				// Then
				expect(r1).toBeFalse();
				expect(r2).toBeTrue();
			});
		});

		describe('|evaluate|', () => {
			it('should verify will return true only when all predicates return true', () => {
				// Given
				const e = SystemEventFilterExpression.of(p1, p2);

				// When
				const r = e.evaluate(c4);

				// Then
				expect(r).toBeTrue();
			});

			it('should verify will return false if one of the Predicates return false', () => {
				// Given
				const e = SystemEventFilterExpression.of(p1, p2, p3);

				// When
				const r = e.evaluate(c4);

				// Then
				expect(r).toBeFalse();
			});
		});
	});
});
