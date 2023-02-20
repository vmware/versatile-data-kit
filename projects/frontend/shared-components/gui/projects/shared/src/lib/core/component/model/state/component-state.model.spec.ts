

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ApiPredicate, ASC, RequestFilterImpl, RequestOrderImpl, RequestPageImpl } from '../../../../common';

import { IDLE, LOADED } from './component-status.model';

import { ComponentState, ComponentStateImpl, LiteralComponentState } from './component-state.model';

describe('ComponentStateImpl', () => {
    let partialStateMock: Partial<ComponentState>;
    let stateMock: ComponentStateImpl;
    let literalStateMock: LiteralComponentState;

    beforeEach(() => {
        const apiPredicate1: ApiPredicate = { sort: ASC, property: 'test.property.10', pattern: 'test.pattern.20' };
        const apiPredicate2: ApiPredicate = { sort: ASC, property: 'test.property.30', pattern: 'test.pattern.40' };

        const uiState1 = { order: 'ASC' };
        const uiState2 = [1, 2, 3];

        const data1 = { data: { name: 'aName' } };
        const data2 = { content: { page: { size: 10, page: 2 } } };

        const dateNowISO = new Date().toISOString();

        partialStateMock = {
            id: 'testId',
            status: LOADED,
            navigationId: 11,
            error: null,
            search: 'testSearch',
            routePath: 'domain/context/entity/10',
            routePathSegments: ['domain/context', 'entity/10'],
            page: new RequestPageImpl(5, 10),
            order: new RequestOrderImpl(apiPredicate1),
            filter: new RequestFilterImpl(apiPredicate2),
            requestParams: new Map<string, any>([
                ['test_param.1', apiPredicate1],
                ['test_param.2', apiPredicate2]
            ]),
            task: `delete_user __ ${ dateNowISO }`,
            uiState: new Map<string, any>([
                ['test_uiState.1', uiState1],
                ['test_uiState.2', uiState2]
            ]),
            data: new Map<string, any>([
                ['test_data.1', data1],
                ['test_data.2', data2]
            ])
        };

        stateMock = new ComponentStateImpl(partialStateMock);

        literalStateMock = {
            id: 'testId',
            status: LOADED,
            navigationId: 11,
            error: null,
            search: 'testSearch',
            routePath: 'domain/context/entity/10',
            routePathSegments: ['domain/context', 'entity/10'],
            page: { pageNumber: 5, pageSize: 10 },
            order: [apiPredicate1],
            filter: [apiPredicate2],
            requestParams: {
                'test_param.1': apiPredicate1,
                'test_param.2': apiPredicate2
            },
            task: `delete_user __ ${ dateNowISO }`,
            uiState: {
                'test_uiState.1': uiState1,
                'test_uiState.2': uiState2
            },
            data: {
                'test_data.1': data1,
                'test_data.2': data2
            }
        };
    });

    it('should verify instance is created', () => {
        // When
        const instance = new ComponentStateImpl({});

        // Then
        expect(instance).toBeDefined();
    });

    it('should verify provided value will be correctly assigned', () => {
        // When
        const instance = new ComponentStateImpl(partialStateMock);

        // Then
        expect(instance.id).toEqual(partialStateMock.id);
        expect(instance.status).toEqual(partialStateMock.status);
        expect(instance.navigationId).toEqual(partialStateMock.navigationId);
        expect(instance.error).toEqual(partialStateMock.error);
        expect(instance.search).toEqual(partialStateMock.search);
        expect(instance.routePath).toEqual(partialStateMock.routePath);
        expect(instance.routePathSegments).toBe(partialStateMock.routePathSegments);
        expect(instance.page).toBe(partialStateMock.page);
        expect(instance.order).toBe(partialStateMock.order);
        expect(instance.filter).toBe(partialStateMock.filter);
        expect(instance.requestParams).toBe(partialStateMock.requestParams);
        expect(instance.task).toEqual(partialStateMock.task);
        expect(instance.uiState).toBe(partialStateMock.uiState);
        expect(instance.data).toBe(partialStateMock.data);
    });

    it('should verify will correctly assign default values', () => {
        // When
        const instance = new ComponentStateImpl({});

        // Then
        expect(instance).toBeDefined();
        expect(instance.id).toBeUndefined();
        expect(instance.status).toEqual(IDLE);
        expect(instance.navigationId).toEqual(null);
        expect(instance.routePath).toBeUndefined();
        expect(instance.routePathSegments).toEqual([]);
        expect(instance.search).toEqual('');
        expect(instance.page).toEqual(RequestPageImpl.empty());
        expect(instance.order).toEqual(RequestOrderImpl.empty());
        expect(instance.filter).toEqual(RequestFilterImpl.empty());
        expect(instance.requestParams).toBeInstanceOf(Map);
        expect(instance.error).toEqual(null);
        expect(instance.task).toEqual(null);
        expect(instance.data).toBeInstanceOf(Map);
        expect(instance.uiState).toBeInstanceOf(Map);
    });

    describe('Statics::', () => {
        describe('Methods::', () => {
            describe('|of|', () => {
                it('should verify factory method will create instance', () => {
                    // When
                    const instance = ComponentStateImpl.of(partialStateMock);

                    // Then
                    expect(instance.id).toEqual(partialStateMock.id);
                    expect(instance.status).toEqual(partialStateMock.status);
                    expect(instance.navigationId).toEqual(partialStateMock.navigationId);
                    expect(instance.error).toEqual(partialStateMock.error);
                    expect(instance.search).toEqual(partialStateMock.search);
                    expect(instance.routePath).toEqual(partialStateMock.routePath);
                    expect(instance.routePathSegments).toBe(partialStateMock.routePathSegments);
                    expect(instance.page).toBe(partialStateMock.page);
                    expect(instance.order).toBe(partialStateMock.order);
                    expect(instance.filter).toBe(partialStateMock.filter);
                    expect(instance.requestParams).toBe(partialStateMock.requestParams);
                    expect(instance.task).toEqual(partialStateMock.task);
                    expect(instance.uiState).toBe(partialStateMock.uiState);
                    expect(instance.data).toBe(partialStateMock.data);
                });
            });

            describe('|fromLiteralComponentState|', () => {
                it('should verify will create instance of ComponentStateImpl from LiteralComponentState', () => {
                    // When
                    const instance = ComponentStateImpl.fromLiteralComponentState(literalStateMock);

                    // Then
                    expect(instance).toEqual(stateMock);
                    expect(instance.order.criteria[0]).toBe(stateMock.order.criteria[0]);
                    expect(instance.filter.criteria[0]).toBe(stateMock.filter.criteria[0]);
                    expect(instance.requestParams.get('test_param.1')).toBe(stateMock.requestParams.get('test_param.1'));
                    expect(instance.requestParams.get('test_param.2')).toBe(stateMock.requestParams.get('test_param.2'));
                    expect(instance.uiState.get('test_uiState.1')).toBe(stateMock.uiState.get('test_uiState.1'));
                    expect(instance.uiState.get('test_uiState.2')).toBe(stateMock.uiState.get('test_uiState.2'));
                    expect(instance.data.get('test_data.1')).toBe(stateMock.data.get('test_data.1'));
                    expect(instance.data.get('test_data.2')).toBe(stateMock.data.get('test_data.2'));
                });
            });

            describe('|cloneDeepLiteral|', () => {
                it('should verify will create deep clone from LiteralComponentState', () => {
                    // When
                    const instance = ComponentStateImpl.cloneDeepLiteral(literalStateMock);

                    // Then
                    expect(instance).toEqual(literalStateMock);
                    expect(instance.order[0]).not.toBe(literalStateMock.order[0]);
                    expect(instance.filter[0]).not.toBe(literalStateMock.filter[0]);
                    expect(instance.requestParams['test_param.1']).not.toBe(literalStateMock.requestParams['test_param.1']);
                    expect(instance.requestParams['test_param.2']).not.toBe(literalStateMock.requestParams['test_param.2']);
                    expect(instance.uiState['test_uiState.1']).not.toBe(literalStateMock.uiState['test_uiState.1']);
                    expect(instance.uiState['test_uiState.2']).not.toBe(literalStateMock.uiState['test_uiState.2']);
                    expect(instance.data['test_data.1']).not.toBe(literalStateMock.data['test_data.1']);
                    expect(instance.data['test_data.2']).not.toBe(literalStateMock.data['test_data.2']);
                });
            });
        });
    });

    describe('Methods::', () => {
        describe('|toLiteral|', () => {
            it('should verify will create LiteralComponentState', () => {
                // When
                const instance = stateMock.toLiteral();

                // Then
                expect(instance).toEqual(literalStateMock);
                expect(instance.order[0]).toBe(literalStateMock.order[0]);
                expect(instance.filter[0]).toBe(literalStateMock.filter[0]);
                expect(instance.requestParams['test_param.1']).toBe(literalStateMock.requestParams['test_param.1']);
                expect(instance.requestParams['test_param.2']).toBe(literalStateMock.requestParams['test_param.2']);
                expect(instance.uiState['test_uiState.1']).toBe(literalStateMock.uiState['test_uiState.1']);
                expect(instance.uiState['test_uiState.2']).toBe(literalStateMock.uiState['test_uiState.2']);
                expect(instance.data['test_data.1']).toBe(literalStateMock.data['test_data.1']);
                expect(instance.data['test_data.2']).toBe(literalStateMock.data['test_data.2']);
            });
        });

        describe('|toLiteralDeepClone|', () => {
            it('should verify will create LiteralComponentState deep cloned', () => {
                // When
                const instance = stateMock.toLiteralDeepClone();

                // Then
                expect(instance).toEqual(literalStateMock);
                expect(instance.order[0]).not.toBe(literalStateMock.order[0]);
                expect(instance.filter[0]).not.toBe(literalStateMock.filter[0]);
                expect(instance.requestParams['test_param.1']).not.toBe(literalStateMock.requestParams['test_param.1']);
                expect(instance.requestParams['test_param.2']).not.toBe(literalStateMock.requestParams['test_param.2']);
                expect(instance.uiState['test_uiState.1']).not.toBe(literalStateMock.uiState['test_uiState.1']);
                expect(instance.uiState['test_uiState.2']).not.toBe(literalStateMock.uiState['test_uiState.2']);
                expect(instance.data['test_data.1']).not.toBe(literalStateMock.data['test_data.1']);
                expect(instance.data['test_data.2']).not.toBe(literalStateMock.data['test_data.2']);
            });
        });

        describe('|copy|', () => {
            it('should verify will create copy from ComponentStateImpl', () => {
                // When
                const instance = stateMock.copy();

                // Then
                expect(instance).not.toBe(stateMock);
                expect(instance).toEqual(stateMock);
            });

            it('should verify will merge provided State on top of original and return instance', () => {
                // Given
                const partialState: Partial<ComponentState> = {
                    id: 'newId',
                    status: LOADED,
                    search: 'randomSearch',
                    routePath: 'domain/context/entity/20',
                    routePathSegments: ['domain/context', 'entity/20'],
                    data: new Map<string, any>(),
                    uiState: new Map<string, any>()
                };

                // When
                const instance = stateMock.copy(partialState);

                // Then
                expect(instance).not.toBe(stateMock);
                expect(instance).not.toEqual(stateMock);
                expect(instance.id).toEqual(partialState.id);
                expect(instance.status).toEqual(partialState.status);
                expect(instance.search).toEqual(partialState.search);
                expect(instance.routePath).toEqual(partialState.routePath);
                expect(instance.routePathSegments).toBe(partialState.routePathSegments);
                expect(instance.data).toBe(partialState.data);
                expect(instance.uiState).toBe(partialState.uiState);
            });
        });
    });
});
