/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/dot-notation,arrow-body-style,prefer-arrow/prefer-arrow-functions */

import { CollectionsUtil } from '../../../../utils';

import { FAILED, IDLE, LOADED, LOADING } from './component-status.model';

import {
	ComponentState,
	ComponentStateImpl,
	LiteralComponentState
} from './component-state.model';

import {
	ComponentsStateHelper,
	LiteralComponentsState
} from './components-state.model';

describe('ComponentsStateHelper', () => {
	it('should verify instance is created', () => {
		// When
		const instance = new ComponentsStateHelper();

		// Then
		expect(instance).toBeDefined();
	});

	describe('Methods::', () => {
		let literalComponentsState: LiteralComponentsState;
		let helper: ComponentsStateHelper;
		let componentState1: ComponentState;
		let componentState2: ComponentState;
		let componentState3: ComponentState;
		let componentState4: ComponentState;

		beforeEach(() => {
			componentState1 = ComponentStateImpl.of({
				id: 'component1',
				status: LOADED
			});
			componentState2 = ComponentStateImpl.of({
				id: 'component2',
				status: IDLE
			});
			componentState3 = ComponentStateImpl.of({
				id: 'component3',
				status: FAILED
			});
			componentState4 = ComponentStateImpl.of({
				id: 'component4',
				status: IDLE
			});

			literalComponentsState = createComponentsLiteralState(
				componentState1,
				componentState2,
				componentState3,
				componentState4
			);

			helper = new ComponentsStateHelper();
			helper.setState(literalComponentsState);
		});

		describe('|getState|', () => {
			it('should verify will return literalComponentState', () => {
				// When
				const state = helper.getState();

				// Then
				expect(state).toBeDefined();
				expect(state).toEqual(literalComponentsState);
				expect(state.components).not.toBe(literalComponentsState.components);
				expect(state.routePathSegments).not.toBe(
					literalComponentsState.routePathSegments
				);
			});
		});

		describe('|getLiteralComponentState|', () => {
			it('should verify will return LiteralComponentState', () => {
				// When
				const state = helper.getLiteralComponentState('component3', [
					'test_domain/context',
					'test_entity/10'
				]);

				// Then
				expect(state).toBeDefined();
				expect(state).toEqual(
					literalComponentsState.routePathSegments['test_domain/context']
						.routePathSegments['test_entity/10'].components['component3']
				);
			});

			it('should verify will return null if there is no such state', () => {
				// When
				const state = helper.getLiteralComponentState('component10', [
					'test_domain/context',
					'test_entity/10'
				]);

				// Then
				expect(state).toEqual(null);
			});

			it('should verify will return null if there is no such routePathSegments', () => {
				// When
				const state = helper.getLiteralComponentState('component3', [
					'test_domain/context',
					'entity/15'
				]);

				// Then
				expect(state).toEqual(null);
			});
		});

		describe('|getComponentState|', () => {
			it('should verify will return ComponentState', () => {
				// When
				const state = helper.getComponentState('component2', [
					'test_domain/context',
					'test_entity/18'
				]);

				// Then
				expect(state).toBeDefined();
				expect(state).toEqual(
					componentState2.copy({
						routePath: 'domain/context/entity/18',
						routePathSegments: ['test_domain/context', 'test_entity/18']
					})
				);
				expect(state.routePathSegments).not.toBe(
					componentState2.routePathSegments
				);
				expect(state.data).not.toBe(componentState2.data);
				expect(state.uiState).not.toBe(componentState2.uiState);
			});

			it('should verify will return null if there is no such state', () => {
				// When
				const state = helper.getComponentState('component4', [
					'test_domain/context'
				]);

				// Then
				expect(state).toEqual(null);
			});

			it('should verify will return null if there is no such routePathSegments', () => {
				// When
				const state = helper.getLiteralComponentState('component2', [
					'domain/explore',
					'test_entity/10'
				]);

				// Then
				expect(state).toEqual(null);
			});
		});

		describe('|getAllComponentState|', () => {
			it('should verify will return Array of all ComponentState in given routePathSegments', () => {
				// When
				const states = helper.getAllComponentState([
					'test_domain/context',
					'test_entity/10'
				]);

				// Then
				expect(states.length).toEqual(8);
				expect(states).toEqual([
					componentState1,
					componentState3,
					componentState2.copy({
						routePath: 'test_domain/context',
						routePathSegments: ['test_domain/context']
					}),
					componentState3.copy({
						routePath: 'test_domain/context',
						routePathSegments: ['test_domain/context']
					}),
					componentState2.copy({
						routePath: 'domain/context/entity/10',
						routePathSegments: ['test_domain/context', 'test_entity/10']
					}),
					componentState4.copy({
						routePath: 'domain/context/entity/10',
						routePathSegments: ['test_domain/context', 'test_entity/10']
					}),
					componentState1.copy({
						routePath: 'domain/context/entity/10',
						routePathSegments: ['test_domain/context', 'test_entity/10']
					}),
					componentState3.copy({
						routePath: 'domain/context/entity/10',
						routePathSegments: ['test_domain/context', 'test_entity/10']
					})
				]);
			});
		});

		describe('|updateLiteralComponentState|', () => {
			it('should verify will update state in right routePathSegments', () => {
				// Given
				const literalState: LiteralComponentState = {
					...componentState1.toLiteral(),
					status: LOADING,
					routePath: 'domain/context/entity/10',
					routePathSegments: ['test_domain/context', 'test_entity/10'],
					data: { payload: { content: { data: [1, 2, 3] } } },
					uiState: { element1: { click: true } }
				};

				// Then 1
				expect(
					helper.getState().routePathSegments['test_domain/context']
						.routePathSegments['test_entity/10'].components['component1']
				).not.toEqual(literalState);

				// When
				helper.updateLiteralComponentState(literalState);

				// Then 2
				expect(
					helper.getState().routePathSegments['test_domain/context']
						.routePathSegments['test_entity/10'].components['component1']
				).toEqual(literalState);
			});
		});

		describe('|resetComponentStates|', () => {
			it('should verify will reset all ComponentStata status in given routePathSegments', () => {
				// When
				helper.resetComponentStates(['test_domain/context', 'test_entity/10']);
				const state = helper.getState();

				// Then
				CollectionsUtil.iterateObject(state.components, (value) => {
					expect(value.status).toEqual(IDLE);
				});

				CollectionsUtil.iterateObject(
					state.routePathSegments['test_domain/context'].components,
					(value) => {
						expect(value.status).toEqual(IDLE);
					}
				);

				CollectionsUtil.iterateObject(
					state.routePathSegments['test_domain/context'].routePathSegments[
						'test_entity/10'
					].components,
					(value) => {
						expect(value.status).toEqual(IDLE);
					}
				);
			});
		});

		describe('|deleteRoutePathSegments|', () => {
			it('should verify will delete routePathSegment', () => {
				// Then 1
				expect(
					helper.getState().routePathSegments['test_domain/context']
						.routePathSegments['test_entity/18']
				).toBeDefined();

				// When
				helper.deleteRoutePathSegments([
					'test_domain/context',
					'test_entity/18'
				]);

				// Then 2
				expect(
					helper.getState().routePathSegments['test_domain/context']
						.routePathSegments['test_entity/18']
				).toBeUndefined();
			});
		});
	});
});

const createComponentsLiteralState = (
	c1: ComponentState,
	c2: ComponentState,
	c3: ComponentState,
	c4: ComponentState
) => {
	return {
		components: {
			component1: { ...c1.toLiteral() },
			component3: { ...c3.toLiteral() }
		},
		routePathSegments: {
			'test_domain/context': {
				components: {
					component2: {
						...c2.toLiteral(),
						routePath: 'test_domain/context',
						routePathSegments: ['test_domain/context']
					},
					component3: {
						...c3.toLiteral(),
						routePath: 'test_domain/context',
						routePathSegments: ['test_domain/context']
					}
				},
				routePathSegments: {
					'test_entity/10': {
						components: {
							component2: {
								...c2.toLiteral(),
								routePath: 'domain/context/entity/10',
								routePathSegments: ['test_domain/context', 'test_entity/10']
							},
							component4: {
								...c4.toLiteral(),
								routePath: 'domain/context/entity/10',
								routePathSegments: ['test_domain/context', 'test_entity/10']
							},
							component1: {
								...c1.toLiteral(),
								routePath: 'domain/context/entity/10',
								routePathSegments: ['test_domain/context', 'test_entity/10']
							},
							component3: {
								...c3.toLiteral(),
								routePath: 'domain/context/entity/10',
								routePathSegments: ['test_domain/context', 'test_entity/10']
							}
						},
						routePathSegments: {}
					},
					'test_entity/18': {
						components: {
							component3: {
								...c3.toLiteral(),
								routePath: 'domain/context/entity/18',
								routePathSegments: ['test_domain/context', 'test_entity/18']
							},
							component2: {
								...c2.toLiteral(),
								routePath: 'domain/context/entity/18',
								routePathSegments: ['test_domain/context', 'test_entity/18']
							},
							component1: {
								...c1.toLiteral(),
								routePath: 'domain/context/entity/18',
								routePathSegments: ['test_domain/context', 'test_entity/18']
							},
							component4: {
								...c4.toLiteral(),
								routePath: 'domain/context/entity/18',
								routePathSegments: ['test_domain/context', 'test_entity/18']
							}
						},
						routePathSegments: {}
					}
				}
			}
		}
	} as LiteralComponentsState;
};
