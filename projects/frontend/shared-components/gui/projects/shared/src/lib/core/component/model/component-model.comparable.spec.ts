

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil } from '../../../utils';

import { ComparableImpl } from '../../../common';

import { RouterState, RouteSegments, RouteState } from '../../router';

import { ComponentState, ComponentStateImpl, IDLE, LOADED } from './state';

import { ComponentModel } from './component.model';

import { ComponentModelComparable } from './component-model.comparable';

describe('ComponentModelComparable', () => {
    it('should verify instance is created', () => {
        // When
        const instance = new ComponentModelComparable(null);

        // Then
        expect(instance).toBeDefined();
    });

    describe('Statics::', () => {
        describe('Methods::', () => {
            describe('|of|', () => {
                it('should verify factory method will create instance', () => {
                    // When
                    const instance = ComponentModelComparable.of(null);

                    // Then
                    expect(instance).toBeInstanceOf(ComponentModelComparable);
                    expect(instance).toBeInstanceOf(ComparableImpl);
                });
            });
        });
    });

    describe('Methods::', () => {
        let componentState: ComponentState;
        let routerState: RouterState;
        let modelComparable: ComponentModelComparable;

        beforeEach(() => {
            componentState = ComponentStateImpl.of({
                id: 'testId',
                status: IDLE,
                data: new Map<string, any>([['countries', ['aCountry', 'bCountry', 'cCountry']]])
            });
            routerState = RouterState.of(
                RouteState.of(
                    RouteSegments.of(
                        'entity/117',
                        {},
                        { entityId: '107' },
                        { search: 'test-team-107' },
                        RouteSegments.of(
                            'domain/context',
                            {},
                            {},
                            { search: 'test-team-107' }
                        )
                    ),
                    'domain/context/entity/117'
                ),
                43
            );
            modelComparable = ComponentModelComparable.of(ComponentModel.of(componentState, routerState));
        });

        describe('|compare|', () => {
            it('should verify will return -1 when stored comparable value is not instance of ComponentModel', () => {
                // Given
                modelComparable = ComponentModelComparable.of(null);

                // When
                const compareV = modelComparable.compare(ComponentModelComparable.of(undefined));

                // Then
                expect(compareV).toEqual(-1);
            });

            it('should verify will return -1 when provided comparable is not instance of expected', () => {
                // When
                const compareV = modelComparable.compare(ComponentModelComparable.of(null));

                // Then
                expect(compareV).toEqual(-1);
            });

            it('should verify will return -1 when no comparable model provided', () => {
                // When
                const compareV = modelComparable.compare(null);

                // Then
                expect(compareV).toEqual(-1);
            });

            it('should verify will return 0 when ComponentModel ref is same', () => {
                // Given
                const isEqualSpy = spyOn(CollectionsUtil, 'isEqual').and.callThrough();

                // When
                modelComparable.value.withPage(10, 100);
                modelComparable.value.getComponentState().uiState.set('submitBtn', { state: 'submitted' });
                const compareV = modelComparable.compare(modelComparable);

                // Then
                expect(compareV).toEqual(0);
                expect(isEqualSpy).not.toHaveBeenCalled();
            });

            it('should verify will return -1 when status is different', () => {
                // Given
                const componentStateComparable = ComponentStateImpl.of({
                    ...componentState,
                    status: LOADED
                });
                const modelComparableDI = ComponentModelComparable.of(ComponentModel.of(componentStateComparable, routerState));

                // When
                const compareV = modelComparable.compare(modelComparableDI);

                // Then
                expect(compareV).toEqual(-1);
            });

            it('should verify will return -1 when task is different', () => {
                // Given
                const componentStateComparable = ComponentStateImpl.of({
                    ...componentState,
                    task: 'patch_entity'
                });
                const modelComparableDI = ComponentModelComparable.of(ComponentModel.of(componentStateComparable, routerState));

                // When
                const compareV = modelComparable.compare(modelComparableDI);

                // Then
                expect(compareV).toEqual(-1);
            });

            it('should verify will return 0 when navigationId is different', () => {
                // Given
                const routerStateComparable = RouterState.of(
                    routerState.state,
                    90
                );
                const modelComparableDI = ComponentModelComparable.of(ComponentModel.of(componentState, routerStateComparable));

                // When
                const compareV = modelComparable.compare(modelComparableDI);

                // Then
                expect(compareV).toEqual(0);
            });

            it('should verify will return -1 when error is different', () => {
                // Given
                const isEqualSpy = spyOn(CollectionsUtil, 'isEqual').and.callThrough();
                const componentStateComparable = ComponentStateImpl.of({
                    ...componentState,
                    error: new Error('new Error()')
                });
                const modelComparableDI = ComponentModelComparable.of(ComponentModel.of(componentStateComparable, routerState));

                // When
                const compareV = modelComparable.compare(modelComparableDI);

                // Then
                expect(compareV).toEqual(-1);
                expect(isEqualSpy).not.toHaveBeenCalled();
            });

            it('should verify will return 0 when data ref is same', () => {
                // Given
                const isEqualSpy = spyOn(CollectionsUtil, 'isEqual').and.callThrough();
                const componentStateComparable = ComponentStateImpl.of({
                    ...componentState,
                    data: componentState.data
                });
                const modelComparableDI = ComponentModelComparable.of(ComponentModel.of(componentStateComparable, routerState));

                // When
                const compareV = modelComparable.compare(modelComparableDI);

                // Then
                expect(compareV).toEqual(0);
                expect(isEqualSpy).not.toHaveBeenCalled();
            });

            it('should verify will return 0 when ref is different but content is same', () => {
                // Given
                const areMapsEqualSpy = spyOn(CollectionsUtil, 'areMapsEqual').and.callThrough();
                const componentStateComparable = ComponentStateImpl.of({
                    ...componentState,
                    data: new Map<string, any>([['countries', ['aCountry', 'bCountry', 'cCountry']]])
                });
                const modelComparableDI = ComponentModelComparable.of(ComponentModel.of(componentStateComparable, routerState));

                // When
                const compareV = modelComparable.compare(modelComparableDI);

                // Then
                expect(compareV).toEqual(0);
                expect(areMapsEqualSpy).toHaveBeenCalledWith(componentState.data, componentStateComparable.data);
            });

            it('should verify will return -1 when ref is different and content is different', () => {
                // Given
                const areMapsEqualSpy = spyOn(CollectionsUtil, 'areMapsEqual').and.callThrough();
                const componentStateComparable = ComponentStateImpl.of({
                    ...componentState,
                    data: new Map<string, any>([
                        ['countries', ['aCountry', 'bCountry', 'cCountry']],
                        ['users', ['aUser', 'bUser', 'cUser']]
                    ])
                });
                const modelComparableDI = ComponentModelComparable.of(ComponentModel.of(componentStateComparable, routerState));

                // When
                const compareV = modelComparable.compare(modelComparableDI);

                // Then
                expect(compareV).toEqual(-1);
                expect(areMapsEqualSpy).toHaveBeenCalledWith(componentState.data, componentStateComparable.data);
            });
        });
    });
});
