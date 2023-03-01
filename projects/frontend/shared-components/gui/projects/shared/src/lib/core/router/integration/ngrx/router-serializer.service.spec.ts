/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { UrlSegment } from '@angular/router';
import { TestBed } from '@angular/core/testing';

import {
	ComponentStub,
	createRouteSnapshot,
	RouteConfigStub
} from '../../../../unit-testing';

import { RouteSegments, RouteState } from '../../model';
import { RouteStateFactory } from '../../factory';

import { SharedRouterSerializer } from './router-serializer.service';

describe('SharedRouterSerializer', () => {
	let service: SharedRouterSerializer;

	beforeEach(() => {
		TestBed.configureTestingModule({
			providers: [SharedRouterSerializer]
		});

		service = TestBed.inject(SharedRouterSerializer);
	});

	it('should verify instance is created', () => {
		// Then
		expect(service).toBeDefined();
	});

	describe('Methods::', () => {
		describe('|serialize|', () => {
			it('should verify will invoke correct methods', () => {
				// Given
				const routeState = RouteState.of(
					RouteSegments.of(
						'delivery',
						{ paramKey: 'prime' },
						{ entityId: 25 },
						{ search: 'test-team' },
						RouteSegments.of(
							'entity/25',
							{ deferredLoading: true },
							{ entityId: 25 },
							{ search: 'test-team' },
							RouteSegments.of(
								'domain/context',
								{ entityKey: 'second' },
								{},
								{ search: 'test-team' },
								null
							)
						)
					),
					'domain/context/entity/25/delivery'
				);
				const factoryCreateSpy = spyOn(
					RouteStateFactory.prototype,
					'create'
				).and.returnValue(routeState);

				const routeSnapshotChild2 = createRouteSnapshot({
					url: [
						new UrlSegment('domain/context', {}),
						new UrlSegment('entity/25', {}),
						new UrlSegment('delivery', {})
					],
					data: { entityKey: 'second' },
					params: { entityId: 25 },
					queryParams: { search: 'team-test' },
					outlet: 'router-outlet',
					component: ComponentStub,
					routeConfig: new RouteConfigStub(
						'delivery',
						ComponentStub,
						'router-outlet'
					)
				});
				const routeSnapshotChild1 = createRouteSnapshot({
					url: [
						new UrlSegment('domain/context', {}),
						new UrlSegment('entity/25', {})
					],
					data: { deferredLoading: true },
					params: { entityId: 25 },
					queryParams: { search: 'team-test' },
					outlet: 'router-outlet',
					component: ComponentStub,
					routeConfig: new RouteConfigStub(
						'entity/25',
						ComponentStub,
						'router-outlet'
					),
					firstChild: routeSnapshotChild2
				});
				const rootRouteSnapshot = createRouteSnapshot({
					url: [new UrlSegment('domain/context', {})],
					data: { paramKey: 'prime' },
					params: {},
					queryParams: { search: 'team-test' },
					outlet: 'router-outlet',
					component: ComponentStub,
					routeConfig: new RouteConfigStub(
						'domain/context',
						ComponentStub,
						'router-outlet'
					),
					firstChild: routeSnapshotChild1
				});

				// When
				const result = service.serialize({
					url: 'domain/context/entity/25/delivery',
					root: rootRouteSnapshot,
					toString: () => ''
				});

				// Then
				expect(factoryCreateSpy).toHaveBeenCalledWith(
					routeSnapshotChild2,
					'domain/context/entity/25/delivery'
				);
				expect(result).toBe(routeState);
			});
		});
	});
});
