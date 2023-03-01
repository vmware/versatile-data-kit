/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
	ApiPredicate,
	RequestFilterImpl,
	RequestOrderImpl,
	RequestPageImpl
} from './request.model';

describe('RequestPage', () => {
	it('should verify instance is created', () => {
		// When
		const instance = new RequestPageImpl(0, 0);

		// Then
		expect(instance).toBeDefined();
		expect(instance).toBeInstanceOf(RequestPageImpl);
	});

	it('should verify correct value are assigned', () => {
		// Given
		const pageNumber = 4;
		const pageSize = 10;

		// When
		const instance = new RequestPageImpl(pageNumber, pageSize);

		// Then
		expect(instance.page).toEqual(pageNumber);
		expect(instance.size).toEqual(pageSize);
	});

	it('should verify on Nil parameters default value will be assigned', () => {
		// When
		const instance = new RequestPageImpl(null, undefined);

		// Then
		expect(instance.page).toEqual(1);
		expect(instance.size).toEqual(25);
	});

	describe('Statics::', () => {
		describe('Methods::', () => {
			describe('|of|', () => {
				it('should verify factory method will create instance', () => {
					// When
					const instance = RequestPageImpl.of(8, 20);

					// Then
					expect(instance).toBeInstanceOf(RequestPageImpl);
					expect(instance.page).toEqual(8);
					expect(instance.size).toEqual(20);
				});
			});

			describe('|empty|', () => {
				it('should verify will create empty instance with default values', () => {
					// When
					const instance = RequestPageImpl.empty();

					// Then
					expect(instance).toBeInstanceOf(RequestPageImpl);
					expect(instance.page).toEqual(1);
					expect(instance.size).toEqual(25);
				});
			});

			describe('|fromLiteral|', () => {
				it('should verify will create new instance from given literal object', () => {
					// Given
					const literal = { pageNumber: 7, pageSize: 52 };

					// When
					const instance = RequestPageImpl.fromLiteral(literal);

					// Then
					expect(instance).toBeInstanceOf(RequestPageImpl);
					expect(instance.page).toEqual(7);
					expect(instance.size).toEqual(52);
				});
			});
		});
	});

	describe('Methods::', () => {
		describe('|toLiteral|', () => {
			it('should verify will create literal object from RequestPage object ', () => {
				// Given
				const requestPage = RequestPageImpl.of(5, 17);

				// When
				const literal = requestPage.toLiteral();

				// Then
				expect(literal).not.toBeInstanceOf(RequestPageImpl);
				expect(literal).toBeInstanceOf(Object);
				expect(literal.pageNumber).toEqual(5);
				expect(literal.pageSize).toEqual(17);
			});
		});

		describe('|toLiteralDeepClone|', () => {
			it('should verify will create literal deep cloned object from RequestPage object ', () => {
				// Given
				const requestPage = RequestPageImpl.of(9, 13);

				// When
				const literal = requestPage.toLiteralDeepClone();

				// Then
				expect(literal).not.toBeInstanceOf(RequestPageImpl);
				expect(literal).toBeInstanceOf(Object);
				expect(literal.pageNumber).toEqual(9);
				expect(literal.pageSize).toEqual(13);
			});
		});
	});
});

describe('RequestOrder', () => {
	let apiPredicate1: ApiPredicate;
	let apiPredicate2: ApiPredicate;
	let apiPredicate3: ApiPredicate;

	beforeEach(() => {
		apiPredicate1 = { pattern: 'test*', property: 'config.team', sort: 'DESC' };
		apiPredicate2 = { pattern: 'mock*', property: 'config.job', sort: 'ASC' };
		apiPredicate3 = {
			pattern: 'prod*',
			property: 'config.status',
			sort: 'DESC'
		};
	});

	it('should verify instance is created', () => {
		// When
		const instance = new RequestOrderImpl();

		// Then
		expect(instance).toBeDefined();
		expect(instance).toBeInstanceOf(RequestOrderImpl);
	});

	it('should verify correct value are assigned', () => {
		// When
		const instance = new RequestOrderImpl(
			apiPredicate1,
			apiPredicate2,
			apiPredicate3
		);

		// Then
		expect(instance.criteria).toBeInstanceOf(Array);
		expect(instance.criteria.length).toEqual(3);
		expect(instance.criteria[0]).toBe(apiPredicate1);
		expect(instance.criteria[1]).toBe(apiPredicate2);
		expect(instance.criteria[2]).toBe(apiPredicate3);
	});

	it('should verify wont assign Nil parameters', () => {
		// When
		const instance = new RequestOrderImpl(
			null,
			apiPredicate2,
			undefined,
			apiPredicate1,
			null,
			apiPredicate3,
			undefined
		);

		// Then
		expect(instance.criteria.length).toEqual(3);
		expect(instance.criteria[0]).toBe(apiPredicate2);
		expect(instance.criteria[1]).toBe(apiPredicate1);
		expect(instance.criteria[2]).toBe(apiPredicate3);
	});

	describe('Statics::', () => {
		describe('Methods::', () => {
			describe('|of|', () => {
				it('should verify factory method will create instance', () => {
					// When
					const instance = RequestOrderImpl.of(
						apiPredicate1,
						null,
						apiPredicate2,
						apiPredicate3
					);

					// Then
					expect(instance).toBeInstanceOf(RequestOrderImpl);
					expect(instance.criteria.length).toEqual(3);
					expect(instance.criteria[0]).toBe(apiPredicate1);
					expect(instance.criteria[1]).toBe(apiPredicate2);
					expect(instance.criteria[2]).toBe(apiPredicate3);
				});
			});

			describe('|empty|', () => {
				it('should verify will create empty instance with no criteria', () => {
					// When
					const instance = RequestOrderImpl.empty();

					// Then
					expect(instance).toBeInstanceOf(RequestOrderImpl);
					expect(instance.criteria).toEqual([]);
				});
			});

			describe('|fromLiteral|', () => {
				it('should verify will create new instance from given literal Array of ApiPredicates', () => {
					// Given
					const literal: ApiPredicate[] = [
						apiPredicate1,
						apiPredicate2,
						apiPredicate3
					];

					// When
					const instance = RequestOrderImpl.fromLiteral(literal);

					// Then
					expect(instance).toBeInstanceOf(RequestOrderImpl);
					expect(instance.criteria.length).toEqual(3);
					expect(instance.criteria[0]).toBe(apiPredicate1);
					expect(instance.criteria[1]).toBe(apiPredicate2);
					expect(instance.criteria[2]).toBe(apiPredicate3);
				});
			});
		});
	});

	describe('Methods::', () => {
		describe('|toLiteral|', () => {
			it('should verify will create literal from RequestOrder object ', () => {
				// Given
				const requestOrder = RequestOrderImpl.of(
					apiPredicate1,
					null,
					apiPredicate2,
					undefined,
					apiPredicate3
				);

				// When
				const literal = requestOrder.toLiteral();

				// Then
				expect(literal).not.toBeInstanceOf(RequestOrderImpl);
				expect(literal).toBeInstanceOf(Array);
				expect(literal[0]).toBe(apiPredicate1);
				expect(literal[1]).toBe(apiPredicate2);
				expect(literal[2]).toBe(apiPredicate3);
			});
		});

		describe('|toLiteralDeepClone|', () => {
			it('should verify will create literal deep cloned from RequestPage object ', () => {
				// Given
				const requestOrder = RequestOrderImpl.of(
					apiPredicate3,
					null,
					apiPredicate1,
					undefined,
					apiPredicate2
				);

				// When
				const literal = requestOrder.toLiteralDeepClone();

				// Then
				expect(literal).not.toBeInstanceOf(RequestOrderImpl);
				expect(literal).toBeInstanceOf(Array);
				expect(literal[0]).not.toBe(apiPredicate3);
				expect(literal[1]).not.toBe(apiPredicate1);
				expect(literal[2]).not.toBe(apiPredicate2);
				expect(literal[0]).toEqual(apiPredicate3);
				expect(literal[1]).toEqual(apiPredicate1);
				expect(literal[2]).toEqual(apiPredicate2);
			});
		});
	});
});

describe('RequestFilter', () => {
	let apiPredicate1: ApiPredicate;
	let apiPredicate2: ApiPredicate;
	let apiPredicate3: ApiPredicate;

	beforeEach(() => {
		apiPredicate1 = { pattern: 'test*', property: 'config.team', sort: 'DESC' };
		apiPredicate2 = { pattern: 'mock*', property: 'config.job', sort: 'ASC' };
		apiPredicate3 = {
			pattern: 'prod*',
			property: 'config.status',
			sort: 'DESC'
		};
	});

	it('should verify instance is created', () => {
		// When
		const instance = new RequestFilterImpl();

		// Then
		expect(instance).toBeDefined();
		expect(instance).toBeInstanceOf(RequestFilterImpl);
	});

	it('should verify correct value are assigned', () => {
		// When
		const instance = new RequestFilterImpl(
			apiPredicate1,
			apiPredicate2,
			apiPredicate3
		);

		// Then
		expect(instance.criteria).toBeInstanceOf(Array);
		expect(instance.criteria.length).toEqual(3);
		expect(instance.criteria[0]).toBe(apiPredicate1);
		expect(instance.criteria[1]).toBe(apiPredicate2);
		expect(instance.criteria[2]).toBe(apiPredicate3);
	});

	it('should verify wont assign Nil parameters', () => {
		// When
		const instance = new RequestFilterImpl(
			null,
			apiPredicate2,
			undefined,
			apiPredicate1,
			null,
			apiPredicate3,
			undefined
		);

		// Then
		expect(instance.criteria.length).toEqual(3);
		expect(instance.criteria[0]).toBe(apiPredicate2);
		expect(instance.criteria[1]).toBe(apiPredicate1);
		expect(instance.criteria[2]).toBe(apiPredicate3);
	});

	describe('Statics::', () => {
		describe('Methods::', () => {
			describe('|of|', () => {
				it('should verify factory method will create instance', () => {
					// When
					const instance = RequestFilterImpl.of(
						apiPredicate1,
						null,
						apiPredicate2,
						apiPredicate3
					);

					// Then
					expect(instance).toBeInstanceOf(RequestFilterImpl);
					expect(instance.criteria.length).toEqual(3);
					expect(instance.criteria[0]).toBe(apiPredicate1);
					expect(instance.criteria[1]).toBe(apiPredicate2);
					expect(instance.criteria[2]).toBe(apiPredicate3);
				});
			});

			describe('|empty|', () => {
				it('should verify will create empty instance with no criteria', () => {
					// When
					const instance = RequestFilterImpl.empty();

					// Then
					expect(instance).toBeInstanceOf(RequestFilterImpl);
					expect(instance.criteria).toEqual([]);
				});
			});

			describe('|fromLiteral|', () => {
				it('should verify will create new instance from given literal Array of ApiPredicates', () => {
					// Given
					const literal: ApiPredicate[] = [
						apiPredicate1,
						apiPredicate2,
						apiPredicate3
					];

					// When
					const instance = RequestFilterImpl.fromLiteral(literal);

					// Then
					expect(instance).toBeInstanceOf(RequestFilterImpl);
					expect(instance.criteria.length).toEqual(3);
					expect(instance.criteria[0]).toBe(apiPredicate1);
					expect(instance.criteria[1]).toBe(apiPredicate2);
					expect(instance.criteria[2]).toBe(apiPredicate3);
				});
			});
		});
	});

	describe('Methods::', () => {
		describe('|toLiteral|', () => {
			it('should verify will create literal from RequestFilter object ', () => {
				// Given
				const requestFilter = RequestFilterImpl.of(
					apiPredicate1,
					null,
					apiPredicate2,
					undefined,
					apiPredicate3
				);

				// When
				const literal = requestFilter.toLiteral();

				// Then
				expect(literal).not.toBeInstanceOf(RequestFilterImpl);
				expect(literal).toBeInstanceOf(Array);
				expect(literal[0]).toBe(apiPredicate1);
				expect(literal[1]).toBe(apiPredicate2);
				expect(literal[2]).toBe(apiPredicate3);
			});
		});

		describe('|toLiteralDeepClone|', () => {
			it('should verify will create literal deep cloned from RequestFilter object ', () => {
				// Given
				const requestFilter = RequestFilterImpl.of(
					apiPredicate3,
					null,
					apiPredicate1,
					undefined,
					apiPredicate2
				);

				// When
				const literal = requestFilter.toLiteralDeepClone();

				// Then
				expect(literal).not.toBeInstanceOf(RequestFilterImpl);
				expect(literal).toBeInstanceOf(Array);
				expect(literal[0]).not.toBe(apiPredicate3);
				expect(literal[1]).not.toBe(apiPredicate1);
				expect(literal[2]).not.toBe(apiPredicate2);
				expect(literal[0]).toEqual(apiPredicate3);
				expect(literal[1]).toEqual(apiPredicate1);
				expect(literal[2]).toEqual(apiPredicate2);
			});
		});
	});
});
