/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/dot-notation */

import { NavigationExtras, Router } from '@angular/router';
import { TestBed } from '@angular/core/testing';

import { of } from 'rxjs';

import { TaurusRouteData } from '../../../common';

import { RouterService, RouteSegments, RouteState } from '../../router';

import { NavigationService } from './navigation.service';

describe('NavigationService', () => {
	let routerStub: jasmine.SpyObj<Router>;
	let routerServiceStub: jasmine.SpyObj<RouterService>;

	let service: NavigationService;

	beforeEach(() => {
		routerStub = jasmine.createSpyObj<Router>('router', ['navigate']);
		routerServiceStub = jasmine.createSpyObj<RouterService>('routerService', [
			'getState',
			'initialize'
		]);

		TestBed.configureTestingModule({
			providers: [
				{ provide: Router, useValue: routerStub },
				{ provide: RouterService, useValue: routerServiceStub },
				NavigationService
			]
		});

		service = TestBed.inject(NavigationService);

		// @ts-ignore
		service['router'] = routerStub;
		// @ts-ignore
		service['routerService'] = routerServiceStub;
	});

	it('should verify instance is created', () => {
		// Then
		expect(service).toBeDefined();
	});

	describe('Methods::()', () => {
		describe('|initialize|', () => {
			it('should verify method exist and is callable', () => {
				// Then
				expect(service.initialize).toBeDefined();
				expect(() => service.initialize()).not.toThrow();
				expect(routerServiceStub.initialize).toHaveBeenCalled();
			});
		});

		describe('|navigate|', () => {
			let url: string;
			let urlChunks: string[];
			let extras: NavigationExtras;

			beforeEach(() => {
				url = '/explore/data-jobs';
				urlChunks = ['explore', 'data-jobs'];
				extras = {
					queryParams: {
						search: 'vdk'
					},
					replaceUrl: true,
					queryParamsHandling: 'merge'
				};
				// @ts-ignore
				service['router'] = routerStub;
			});

			it('should verify will call Router.navigate() from Angular', () => {
				// Given
				routerStub.navigate.and.returnValue(Promise.resolve(true));

				// When
				service.navigate(url);

				// Then
				expect(routerStub.navigate).toHaveBeenCalledWith([
					'/explore',
					'data-jobs'
				]);
			});

			it('should verify will return Promise', () => {
				// Given
				routerStub.navigate.and.returnValue(Promise.resolve(true));

				// When
				const returnedValue = service.navigate(url);

				// Then
				expect(returnedValue).toBeInstanceOf(Promise);
			});

			it('should verify will return Promise.resolve(false) on Nil value for url', () => {
				// When
				const returnedValue = service.navigate(null);

				// Then
				returnedValue.then((v) => expect(v).toBeFalse());
				expect(routerStub.navigate).not.toHaveBeenCalled();
			});

			it('should verify will handle both url string and url Array', () => {
				// Given
				routerStub.navigate.and.returnValue(Promise.resolve(true));

				// When
				service.navigate(url);
				service.navigate(urlChunks);

				// Then
				expect(routerStub.navigate).toHaveBeenCalledTimes(2);
				expect(routerStub.navigate.calls.argsFor(0)).toEqual([
					['/explore', 'data-jobs']
				]);
				expect(routerStub.navigate.calls.argsFor(1)).toEqual([
					['/explore', 'data-jobs']
				]);
			});

			it('should verify will handle extras parameters', () => {
				// Given
				routerStub.navigate.and.returnValue(Promise.resolve(true));

				// When
				service.navigate(url, extras);

				// Then
				expect(routerStub.navigate).toHaveBeenCalledWith(
					['/explore', 'data-jobs'],
					extras
				);
			});
		});

		describe('|_navigationSystemEventHandler_|', () => {
			it('should verify will skip navigation if payload is Nil', () => {
				// Given
				const payload: { url: string | string[]; extras?: NavigationExtras } =
					null;
				const navigateSpy = spyOn(service, 'navigate').and.callFake(() =>
					Promise.resolve(false)
				);

				// When
				const returnedValue = service._navigationSystemEventHandler_(payload);

				// Then
				returnedValue.then((v) => expect(v).toBeFalse());
				expect(navigateSpy).not.toHaveBeenCalled();
			});

			it('should verify will execute navigation when payload is provided', () => {
				// Given
				const payload = {
					url: '/explore/data-jobs',
					extras: { queryParams: { search: 'vdk' } }
				};
				spyOn(service, 'navigate').and.callFake(() => Promise.resolve(true));

				// When
				const returnedValue = service._navigationSystemEventHandler_(payload);

				// Then
				returnedValue.then((v) => expect(v).toBeTrue());
				expect(service.navigate).toHaveBeenCalledWith(
					payload.url,
					payload.extras
				);
			});
		});

		describe('|navigateBack|', () => {
			it('should verify will invoke correct methods when NavigationAction provided', (done) => {
				// Given
				const routeState = RouteState.of(
					RouteSegments.of(
						'delivery',
						{
							navigateBack: {
								path: '$.parent',
								queryParamsHandling: 'preserve',
								queryParams: { randomParam: 'abc' }
							}
						} as TaurusRouteData,
						{},
						{ search: 'team-test' },
						RouteSegments.of(
							'entity/25',
							{
								navigateTo: {
									path: '/domain/context/entity/{0}/update/information',
									replacers: [{ searchValue: '{0}', replaceValue: '$.entity' }],
									queryParams: { showWizard: true }
								}
							} as TaurusRouteData,
							{ entityId: 25 },
							{ search: 'team-test' },
							RouteSegments.of(
								'domain/context',
								{},
								{},
								{ search: 'team-test' },
								null,
								'domain/context'
							),
							'entity/:entityId'
						),
						'delivery'
					),
					'domain/context/entity/25/delivery'
				);
				routerServiceStub.getState.and.returnValue(of(routeState));
				const navigateSpy = spyOn(service, 'navigate').and.returnValue(
					Promise.resolve(true)
				);

				// When
				const promise = service.navigateBack();

				// Then
				expect(promise).toBeInstanceOf(Promise);
				expect(routerServiceStub.getState).toHaveBeenCalled();
				promise.then((value) => {
					expect(value).toBeTrue();
					expect(navigateSpy).toHaveBeenCalledWith(
						'/domain/context/entity/25',
						{
							queryParamsHandling: 'preserve'
						}
					);

					done();
				});
			});

			it('should verify will invoke correct methods when no NavigationAction provided', (done) => {
				// Given
				const routeState = RouteState.of(
					RouteSegments.of(
						'delivery',
						{},
						{},
						{ search: 'team-test' },
						RouteSegments.of(
							'entity/25',
							{},
							{ entityId: 25 },
							{ search: 'team-test' },
							RouteSegments.of(
								'domain/context',
								{},
								{},
								{ search: 'team-test' },
								null,
								'domain/context'
							),
							'entity/:entityId'
						),
						'delivery'
					),
					'domain/context/entity/25/delivery'
				);
				routerServiceStub.getState.and.returnValue(of(routeState));
				const navigateSpy = spyOn(service, 'navigate').and.returnValue(
					Promise.resolve(true)
				);

				// When
				const promise = service.navigateBack();

				// Then
				expect(promise).toBeInstanceOf(Promise);
				expect(routerServiceStub.getState).toHaveBeenCalled();
				promise.then((value) => {
					expect(value).toBeTrue();
					expect(navigateSpy).toHaveBeenCalledWith(
						'/domain/context/entity/25',
						{
							queryParamsHandling: 'merge'
						}
					);

					done();
				});
			});
		});

		describe('|navigateTo|', () => {
			it('should verify will invoke correct methods preserve routerState QueryParams', (done) => {
				// Given
				const routeState = RouteState.of(
					RouteSegments.of(
						'delivery',
						{
							navigateBack: {
								path: '$.parent',
								queryParamsHandling: 'preserve',
								queryParams: { randomParam: 'abc' }
							}
						} as TaurusRouteData,
						{},
						{ search: 'team-test' },
						RouteSegments.of(
							'entity/25',
							{
								navigateTo: {
									path: '/domain/context/entity/{0}/update/information',
									replacers: [{ searchValue: '{0}', replaceValue: '$.entity' }],
									queryParamsHandling: 'preserve',
									queryParams: { showWizard: true }
								}
							} as TaurusRouteData,
							{ entityId: 25 },
							{ search: 'team-test' },
							RouteSegments.of(
								'domain/context',
								{},
								{},
								{ search: 'team-test' },
								null,
								'domain/context'
							),
							'entity/:entityId'
						),
						'delivery'
					),
					'domain/context/entity/25/delivery'
				);
				routerServiceStub.getState.and.returnValue(of(routeState));
				const navigateSpy = spyOn(service, 'navigate').and.returnValue(
					Promise.resolve(true)
				);

				// When
				const promise = service.navigateTo({ '$.entity': '101' });

				// Then
				expect(promise).toBeInstanceOf(Promise);
				expect(routerServiceStub.getState).toHaveBeenCalled();
				promise.then((value) => {
					expect(value).toBeTrue();
					expect(navigateSpy).toHaveBeenCalledWith(
						'/domain/context/entity/101/update/information',
						{
							queryParamsHandling: 'preserve'
						}
					);

					done();
				});
			});

			it('should verify will invoke correct methods merge QueryParams, provided and from routeState', (done) => {
				// Given
				const routeState = RouteState.of(
					RouteSegments.of(
						'delivery',
						{
							navigateBack: {
								path: '$.parent',
								queryParamsHandling: 'preserve',
								queryParams: { randomParam: 'abc' }
							}
						} as TaurusRouteData,
						{},
						{ search: 'team-test' },
						RouteSegments.of(
							'entity/25',
							{
								navigateTo: {
									path: '/domain/context/entity/{0}/update/information',
									replacers: [{ searchValue: '{0}', replaceValue: '$.entity' }],
									queryParams: { showWizard: true },
									queryParamsHandling: 'merge'
								}
							} as TaurusRouteData,
							{ entityId: 25 },
							{ search: 'team-test' },
							RouteSegments.of(
								'domain/context',
								{},
								{},
								{ search: 'team-test' },
								null,
								'domain/context'
							),
							'entity/:entityId'
						),
						'delivery'
					),
					'domain/context/entity/25/delivery'
				);
				routerServiceStub.getState.and.returnValue(of(routeState));
				const navigateSpy = spyOn(service, 'navigate').and.returnValue(
					Promise.resolve(true)
				);

				// When
				const promise = service.navigateTo({ '$.entity': '101' });

				// Then
				expect(promise).toBeInstanceOf(Promise);
				expect(routerServiceStub.getState).toHaveBeenCalled();
				promise.then((value) => {
					expect(value).toBeTrue();
					expect(navigateSpy).toHaveBeenCalledWith(
						'/domain/context/entity/101/update/information',
						{
							queryParamsHandling: 'merge',
							queryParams: { search: 'team-test', showWizard: true }
						}
					);

					done();
				});
			});

			it('should verify will reject Promise when no NavigationAction is provided', (done) => {
				// Given
				const routeState = RouteState.of(
					RouteSegments.of(
						'delivery',
						{},
						{},
						{ search: 'team-test' },
						null,
						'delivery'
					),
					'domain/context/entity/25/delivery'
				);
				routerServiceStub.getState.and.returnValue(of(routeState));
				const navigateSpy = spyOn(service, 'navigate').and.returnValue(
					Promise.resolve(true)
				);
				const consoleErrorSpy = spyOn(console, 'error').and.callThrough();

				// When
				const promise = service.navigateTo();

				// Then
				expect(promise).toBeInstanceOf(Promise);
				expect(routerServiceStub.getState).toHaveBeenCalled();
				promise.then((value) => {
					expect(value).toBeFalse();
					expect(navigateSpy).not.toHaveBeenCalled();
					expect(consoleErrorSpy).toHaveBeenCalled();

					done();
				});
			});
		});
	});
});
