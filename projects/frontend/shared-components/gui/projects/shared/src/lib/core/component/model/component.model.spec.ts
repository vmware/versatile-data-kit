/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ASC, RequestFilterImpl, RequestPageImpl } from '../../../common';

import { RouterState, RouteSegments, RouteState } from '../../router';

import {
	ComponentState,
	ComponentStateImpl,
	FAILED,
	IDLE,
	INITIALIZED,
	LOADED,
	LOADING
} from './state';

import { ComponentModel } from './component.model';

import { ComponentModelComparable } from './component-model.comparable';

describe('ComponentModel', () => {
	it('should verify instance is created', () => {
		// When
		const instance = new ComponentModel(null, null);

		// Then
		expect(instance).toBeDefined();
	});

	describe('Statics::', () => {
		describe('Methods::()', () => {
			describe('|of|', () => {
				it('should verify factory method will create instance', () => {
					// Given
					const componentState = {
						id: 'testId',
						status: IDLE
					} as ComponentState;
					const routerState = RouterState.of(
						{
							routeSegments: {
								routePath: 'domain/context'
							}
						} as RouteState,
						9
					);

					// When
					const instance = ComponentModel.of(componentState, routerState);

					// Then
					expect(instance).toBeInstanceOf(ComponentModel);
				});
			});
		});
	});

	describe('Getters/Setters::', () => {
		let componentState: ComponentState;
		let routerState: RouterState;

		beforeEach(() => {
			componentState = { id: 'testId', status: IDLE } as ComponentState;
			routerState = RouterState.of(
				{
					routeSegments: {
						routePath: 'domain/context'
					}
				} as RouteState,
				9
			);
		});

		describe('|GET -> routerState|', () => {
			it('should verify will return correct value', () => {
				// Given
				const model = ComponentModel.of(componentState, routerState);

				// When
				const _routerState = model.routerState;

				// Then
				expect(_routerState).toBe(routerState);
			});
		});

		describe('|GET -> status|', () => {
			it('should verify will return correct value', () => {
				// Given
				const model = ComponentModel.of(componentState, routerState);

				// When
				const status = model.status;

				// Then
				expect(status).toEqual(IDLE);
			});
		});

		describe('|GET -> routePath|', () => {
			it('should verify will return correct value from componentState', () => {
				// Given
				componentState = { ...componentState, routePath: 'entity/15' };
				const model = ComponentModel.of(componentState, routerState);

				// When
				const routePath = model.routePath;

				// Then
				expect(routePath).toEqual('entity/15');
			});

			it('should verify will return correct value from routerState', () => {
				// Given
				const model = ComponentModel.of(componentState, routerState);

				// When
				const routePath = model.routePath;

				// Then
				expect(routePath).toEqual('domain/context');
			});
		});
	});

	describe('Methods::', () => {
		let componentState: ComponentState;
		let routerState: RouterState;
		let model: ComponentModel;

		beforeEach(() => {
			componentState = ComponentStateImpl.of({
				id: 'testId',
				status: IDLE,
				data: new Map<string, any>([
					['countries', ['aCountry', 'bCountry', 'cCountry']]
				])
			});
			routerState = RouterState.of(
				RouteState.of(
					RouteSegments.of(
						'entity/21',
						{ entityId: '21' },
						{ search: 'test-team' },
						RouteSegments.of('domain/context', {}, { search: 'test-team' })
					),
					'domain/context/entity/21'
				),
				9
			);
			model = ComponentModel.of(componentState, routerState);
		});

		describe('|getComponentState|', () => {
			it('should verify will return ComponentState', () => {
				// When
				const _componentState = model.getComponentState();

				// Then
				expect(_componentState).toBe(componentState);
			});
		});

		describe('|withSearch|', () => {
			it('should verify will invoke correct method with correct payload', () => {
				// Given
				const updateSpy = spyOn(
					model,
					'updateComponentState'
				).and.callThrough();

				// When
				const ref = model.withSearch('metadataSearchParam');

				// Then
				expect(ref).toBe(model);
				expect(updateSpy).toHaveBeenCalledWith({
					search: 'metadataSearchParam'
				});
			});
		});

		describe('|withPage|', () => {
			it('should verify will invoke correct method with correct payload', () => {
				// Given
				const updateSpy = spyOn(
					model,
					'updateComponentState'
				).and.callThrough();

				// When
				const ref = model.withPage(6, 18);

				// Then
				expect(ref).toBe(model);
				expect(updateSpy).toHaveBeenCalledWith({
					page: RequestPageImpl.of(6, 18)
				});
			});
		});

		describe('|withFilter|', () => {
			it('should verify will invoke correct method with correct payload', () => {
				// Given
				const updateSpy = spyOn(
					model,
					'updateComponentState'
				).and.callThrough();

				// When
				const ref = model.withFilter([
					{ pattern: 'test*', property: 'config.path', sort: ASC }
				]);

				// Then
				expect(ref).toBe(model);
				expect(updateSpy).toHaveBeenCalledWith({
					filter: RequestFilterImpl.of({
						pattern: 'test*',
						property: 'config.path',
						sort: ASC
					})
				});
			});
		});

		describe('|withRequestParam|', () => {
			it('should verify will set data to Request param map', () => {
				// Given
				const attributes = ['topBrand', 'extraSize', 'largeNumber'];
				const order = { sort: ASC, path: 'config.user' };

				// When
				const ref = model
					.withRequestParam('attributes', attributes)
					.withRequestParam('order', order);

				// Then
				expect(ref).toBe(model);
				expect(model.getComponentState().requestParams).toEqual(
					new Map<string, any>([
						['attributes', [...attributes]],
						['order', { ...order }]
					])
				);
			});
		});

		describe('|withData|', () => {
			it('should verify will set data to Data map', () => {
				// Given
				const users = ['aUser', 'bUser', 'cUser'];

				// When
				const ref = model.withData('users', users);

				// Then
				expect(ref).toBe(model);
				expect(model.getComponentState().data).toEqual(
					new Map<string, any>([
						['countries', ['aCountry', 'bCountry', 'cCountry']],
						['users', users]
					])
				);
			});
		});

		describe('|withTask|', () => {
			it('should verify will set Task to ComponentState', () => {
				// Given
				const task = 'delete_entity';

				// Then 1
				expect(model.getComponentState().task).not.toEqual(task);

				// When
				const ref = model.withTask(task);

				// Then 2
				expect(ref).toBe(model);
				expect(model.getComponentState().task).toEqual(task);
			});
		});

		describe('|getTask|', () => {
			it('should verify will return Task from ComponentState', () => {
				// Given
				const task = 'search_users';
				const taskIdentifier = `${task} __ ${new Date().toISOString()}`;
				componentState = ComponentStateImpl.of({
					...componentState,
					task: taskIdentifier
				});
				model = ComponentModel.of(componentState, routerState);

				// When
				const res = model.getTask();

				// Then
				expect(res).toBe(task);
			});
		});

		describe('|withError|', () => {
			it('should verify will invoke correct method with correct payload', () => {
				// Given
				const error = new Error('random error');
				const updateSpy = spyOn(
					model,
					'updateComponentState'
				).and.callThrough();

				// When
				const ref = model.withError(error);

				// Then
				expect(ref).toBe(model);
				expect(updateSpy).toHaveBeenCalledWith({ error });
			});
		});

		describe('|clearError|', () => {
			it('should verify will invoke correct method with correct payload', () => {
				// Given
				const updateSpy = spyOn(
					model,
					'updateComponentState'
				).and.callThrough();

				// When
				const ref = model.clearError();

				// Then
				expect(ref).toBe(model);
				expect(updateSpy).toHaveBeenCalledWith({ error: null });
			});
		});

		describe('|withUiState|', () => {
			it('should verify will set data to Data map', () => {
				// Given
				const btnState = { active: true };

				// When
				const ref = model.withUiState('btnOk', btnState);

				// Then
				expect(ref).toBe(model);
				expect(model.getComponentState().uiState).toEqual(
					new Map<string, any>([['btnOk', btnState]])
				);
			});
		});

		describe('|getUiState|', () => {
			it('should verify will return uiState from ComponentState for given key', () => {
				// Given
				const btnState = { active: true };
				componentState = ComponentStateImpl.of({
					...componentState,
					uiState: new Map<string, any>([['btnOk', btnState]])
				});
				model = ComponentModel.of(componentState, routerState);

				// When
				const uiState = model.getUiState('btnOk');

				// Then
				expect(uiState).toBe(btnState);
			});
		});

		describe('|withStatusIdle|', () => {
			it('should verify will invoke correct method with correct payload', () => {
				// Given
				const updateSpy = spyOn(
					model,
					'updateComponentState'
				).and.callThrough();

				// When
				const ref = model.withStatusIdle();

				// Then
				expect(ref).toBe(model);
				expect(updateSpy).toHaveBeenCalledWith({ status: IDLE });
			});
		});

		describe('|withStatusLoading|', () => {
			it('should verify will invoke correct method with correct payload', () => {
				// Given
				const updateSpy = spyOn(
					model,
					'updateComponentState'
				).and.callThrough();

				// When
				const ref = model.withStatusLoading();

				// Then
				expect(ref).toBe(model);
				expect(updateSpy).toHaveBeenCalledWith({ status: LOADING });
			});
		});

		describe('|withStatusLoaded|', () => {
			it('should verify will invoke correct method with correct payload', () => {
				// Given
				const updateSpy = spyOn(
					model,
					'updateComponentState'
				).and.callThrough();

				// When
				const ref = model.withStatusLoaded();

				// Then
				expect(ref).toBe(model);
				expect(updateSpy).toHaveBeenCalledWith({ status: LOADED });
			});
		});

		describe('|withStatusFailed|', () => {
			it('should verify will invoke correct method with correct payload', () => {
				// Given
				const updateSpy = spyOn(
					model,
					'updateComponentState'
				).and.callThrough();

				// When
				const ref = model.withStatusFailed();

				// Then
				expect(ref).toBe(model);
				expect(updateSpy).toHaveBeenCalledWith({ status: FAILED });
			});
		});

		describe('|updateComponentState|', () => {
			it('should verify will update local ComponentState', () => {
				// Given
				const assertionComponentState = ComponentStateImpl.of({
					...componentState,
					status: INITIALIZED,
					id: 'test-component-1234',
					search: 'teamUSA*',
					page: RequestPageImpl.of(9, 45)
				});

				// When
				const ref = model.updateComponentState({
					status: INITIALIZED,
					id: 'test-component-1234',
					search: 'teamUSA*',
					page: RequestPageImpl.of(9, 45)
				});

				// Then
				expect(ref).toBe(model);
				expect(model.getComponentState()).toEqual(assertionComponentState);
			});
		});

		describe('|isModified|', () => {
			it('should verify will invoke correct methods', () => {
				// Given
				const componentModelComparableStub =
					jasmine.createSpyObj<ComponentModelComparable>('comparable', [
						'notEqual'
					]);
				componentModelComparableStub.notEqual.and.returnValue(false);
				const factoryOfSpy = spyOn(
					ComponentModelComparable,
					'of'
				).and.returnValue(componentModelComparableStub);

				const comparableState = ComponentStateImpl.of({
					...componentState,
					data: new Map<string, any>([
						['countries', ['aCountry', 'bCountry', 'cCountry']],
						['users', ['aUser', 'bUser', 'cUser']]
					])
				});
				const comparableModel = ComponentModel.of(comparableState, routerState);

				// When
				const isModified = model.isModified(comparableModel);

				// Then
				expect(isModified).toBeFalse();
				expect(factoryOfSpy).toHaveBeenCalledTimes(2);
				expect(factoryOfSpy.calls.argsFor(0)).toEqual([model]);
				expect(factoryOfSpy.calls.argsFor(1)).toEqual([comparableModel]);
				expect(componentModelComparableStub.notEqual).toHaveBeenCalledTimes(1);
				expect(componentModelComparableStub.notEqual).toHaveBeenCalledWith(
					componentModelComparableStub
				);
			});
		});
	});
});
