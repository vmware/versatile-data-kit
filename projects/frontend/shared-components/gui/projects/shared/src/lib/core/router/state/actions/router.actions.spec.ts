/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { BaseAction, BaseActionWithPayload } from '../../../ngrx';

import {
	LOCATION_BACK,
	LOCATION_FORWARD,
	LOCATION_GO,
	LocationBack,
	LocationForward,
	LocationGo,
	ROUTER_NAVIGATE,
	RouterNavigate
} from './router.actions';

describe('NavigationActions', () => {
	describe('RouterNavigate', () => {
		it('should verify instance is created', () => {
			// Then
			expect(
				() => new RouterNavigate({ commands: [], extras: {} })
			).toBeDefined();
		});

		it('should verify correct type is assigned', () => {
			// When
			const instance = new RouterNavigate({ commands: [], extras: {} });

			// Then
			expect(instance.type).toEqual(ROUTER_NAVIGATE);
		});

		it('should verify prototype chaining', () => {
			// When
			const instance = new RouterNavigate({ commands: [], extras: {} });

			// Then
			expect(instance).toBeInstanceOf(BaseActionWithPayload);
			expect(instance).toBeInstanceOf(BaseAction);
		});

		describe('Statics::', () => {
			describe('Methods::', () => {
				describe('|of|', () => {
					it('should verify factory method will create instance', () => {
						// When
						const instance = RouterNavigate.of({ commands: [], extras: {} });

						// Then
						expect(instance).toBeInstanceOf(RouterNavigate);
					});
				});
			});
		});
	});

	describe('LocationGo', () => {
		it('should verify instance is created', () => {
			// Then
			expect(
				() =>
					new LocationGo({
						path: 'entity/15',
						query: 'search=test-team',
						state: {}
					})
			).toBeDefined();
		});

		it('should verify correct type is assigned', () => {
			// When
			const instance = new LocationGo({
				path: 'entity/15',
				query: 'search=test-team',
				state: {}
			});

			// Then
			expect(instance.type).toEqual(LOCATION_GO);
		});

		it('should verify prototype chaining', () => {
			// When
			const instance = new LocationGo({
				path: 'entity/15',
				query: 'search=test-team',
				state: {}
			});

			// Then
			expect(instance).toBeInstanceOf(BaseActionWithPayload);
			expect(instance).toBeInstanceOf(BaseAction);
		});

		describe('Statics::', () => {
			describe('Methods::', () => {
				describe('|of|', () => {
					it('should verify factory method will create instance', () => {
						// When
						const instance = LocationGo.of({
							path: 'entity/15',
							query: 'search=test-team',
							state: {}
						});

						// Then
						expect(instance).toBeInstanceOf(LocationGo);
					});
				});
			});
		});
	});

	describe('LocationBack', () => {
		it('should verify instance is created', () => {
			// Then
			expect(() => new LocationBack()).toBeDefined();
		});

		it('should verify correct type is assigned', () => {
			// When
			const instance = new LocationBack();

			// Then
			expect(instance.type).toEqual(LOCATION_BACK);
		});

		it('should verify prototype chaining', () => {
			// When
			const instance = new LocationBack();

			// Then
			expect(instance).toBeInstanceOf(BaseAction);
		});

		describe('Statics::', () => {
			describe('Methods::', () => {
				describe('|of|', () => {
					it('should verify factory method will create instance', () => {
						// When
						const instance = LocationBack.of();

						// Then
						expect(instance).toBeInstanceOf(LocationBack);
					});
				});
			});
		});
	});

	describe('LocationForward', () => {
		it('should verify instance is created', () => {
			// Then
			expect(() => new LocationForward()).toBeDefined();
		});

		it('should verify correct type is assigned', () => {
			// When
			const instance = new LocationForward();

			// Then
			expect(instance.type).toEqual(LOCATION_FORWARD);
		});

		it('should verify prototype chaining', () => {
			// When
			const instance = new LocationForward();

			// Then
			expect(instance).toBeInstanceOf(BaseAction);
		});

		describe('Statics::', () => {
			describe('Methods::', () => {
				describe('|of|', () => {
					it('should verify factory method will create instance', () => {
						// When
						const instance = LocationForward.of();

						// Then
						expect(instance).toBeInstanceOf(LocationForward);
					});
				});
			});
		});
	});
});
