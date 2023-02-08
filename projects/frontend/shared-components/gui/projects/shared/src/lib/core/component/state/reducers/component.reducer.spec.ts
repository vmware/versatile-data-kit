

/* eslint-disable arrow-body-style,prefer-arrow/prefer-arrow-functions */

import { ROUTER_NAVIGATION, RouterNavigationPayload } from '@ngrx/router-store';

import { CallFake } from '../../../../unit-testing';

import { CollectionsUtil } from '../../../../utils';

import { BaseActionWithPayload } from '../../../ngrx';

import { RouteSegments, RouteState } from '../../../router';

import {
    ComponentsStateHelper,
    ComponentState,
    FAILED,
    IDLE,
    INITIALIZED,
    LiteralComponentsState,
    LiteralComponentState,
    LOADED,
    LOADING,
    StatusType
} from '../../model';

import {
    COMPONENT_CLEAR_DATA,
    COMPONENT_FAILED,
    COMPONENT_INIT,
    COMPONENT_LOADING,
    COMPONENT_UPDATE,
    ComponentIdle,
    ComponentLoaded
} from '../actions';

import { componentReducer } from './component.reducer';

describe('componentReducer', () => {
    let id: string;
    let routePathSegments: string[];
    let literalComponentsState: LiteralComponentsState;
    let updateComponentHelperSpy: jasmine.Spy;
    let getComponentHelperSpy: jasmine.Spy;
    let getStateHelperSpy: jasmine.Spy;

    beforeEach(() => {
        id = 'testComponent1';
        routePathSegments = ['test_entity/15'];
        literalComponentsState = {
            components: {},
            routePathSegments: {}
        };
        updateComponentHelperSpy = spyOn(ComponentsStateHelper.prototype, 'updateLiteralComponentState').and.callFake(CallFake);
        getComponentHelperSpy = spyOn(ComponentsStateHelper.prototype, 'getLiteralComponentState');
        getStateHelperSpy = spyOn(ComponentsStateHelper.prototype, 'getState');
    });

    describe('Actions::', () => {
        describe('|COMPONENT_INIT|', () => {
            it('should verify invokes correct methods', () => {
                // Given
                const action = new ActionStub<ComponentState>(COMPONENT_INIT, createComponentState(null));
                getStateHelperSpy
                    .and
                    .returnValue(createComponentsState(createComponentState(INITIALIZED).toLiteral()));

                // When
                const result = componentReducer(literalComponentsState, action);

                // Then
                expect(result).toEqual(createComponentsState(createComponentState(INITIALIZED).toLiteral()));
                expect(updateComponentHelperSpy).toHaveBeenCalledWith(createComponentState(INITIALIZED).toLiteral());
            });
        });

        describe('|COMPONENT_IDLE|', () => {
            it('should verify invokes correct methods', () => {
                // Given
                const action = ComponentIdle.of(createComponentState(INITIALIZED, 'test-team', 4));
                getComponentHelperSpy
                    .and
                    .returnValue(createComponentState(INITIALIZED).toLiteral());
                getStateHelperSpy
                    .and
                    .returnValue(createComponentsState(createComponentState(IDLE, 'test-team', 4).toLiteral()));

                // When
                const result = componentReducer(literalComponentsState, action);

                // Then
                expect(getComponentHelperSpy).toHaveBeenCalledWith(id, routePathSegments);
                expect(result).toEqual(createComponentsState(createComponentState(IDLE, 'test-team', 4).toLiteral()));
                expect(updateComponentHelperSpy).toHaveBeenCalledWith(createComponentState(IDLE, 'test-team', 4).toLiteral());
            });
        });

        describe('|COMPONENT_LOADING|', () => {
            it('should verify invokes correct methods', () => {
                // Given
                const action = new ActionStub<ComponentState>(COMPONENT_LOADING, createComponentState(IDLE, 'test-team', 4));
                getComponentHelperSpy
                    .and
                    .returnValue(createComponentState(IDLE).toLiteral());
                getStateHelperSpy
                    .and
                    .returnValue(createComponentsState(createComponentState(LOADING, 'test-team', 4).toLiteral()));

                // When
                const result = componentReducer(literalComponentsState, action);

                // Then
                expect(getComponentHelperSpy).toHaveBeenCalledWith(id, routePathSegments);
                expect(result).toEqual(createComponentsState(createComponentState(LOADING, 'test-team', 4).toLiteral()));
                expect(updateComponentHelperSpy).toHaveBeenCalledWith(createComponentState(LOADING, 'test-team', 4).toLiteral());
            });
        });

        describe('|COMPONENT_UPDATE|', () => {
            it('should verify invokes correct methods (data from action)', () => {
                // Given
                const data = new Map<string, any>([['users', []], ['cities', {}]]);
                const action = new ActionStub<ComponentState>(
                    COMPONENT_UPDATE,
                    createComponentState(IDLE, 'test-team', 7, data)
                );
                getComponentHelperSpy
                    .and
                    .returnValue(createComponentState(LOADING).toLiteral());
                getStateHelperSpy
                    .and
                    .returnValue(
                        createComponentsState(
                            createComponentState(IDLE, 'test-team', 7, data).toLiteral()
                        )
                    );

                // When
                const result = componentReducer(literalComponentsState, action);

                // Then
                expect(getComponentHelperSpy).toHaveBeenCalledWith(id, routePathSegments);
                expect(result).toEqual(
                    createComponentsState(
                        createComponentState(IDLE, 'test-team', 7, data).toLiteral()
                    )
                );
                expect(updateComponentHelperSpy).toHaveBeenCalledWith(
                    createComponentState(IDLE, 'test-team', 7, data).toLiteral()
                );
            });

            it('should verify invokes correct methods (data from store)', () => {
                // Given
                const data = new Map<string, any>([['countries', []], ['payload', {}]]);
                const action = new ActionStub<ComponentState>(
                    COMPONENT_UPDATE,
                    createComponentState(FAILED, 'test-team', 6)
                );
                getComponentHelperSpy
                    .and
                    .returnValue(createComponentState(LOADING, 'test-team', 4, data).toLiteral());
                getStateHelperSpy
                    .and
                    .returnValue(
                        createComponentsState(
                            createComponentState(FAILED, 'test-team', 6, data).toLiteral()
                        )
                    );

                // When
                const result = componentReducer(literalComponentsState, action);

                // Then
                expect(getComponentHelperSpy).toHaveBeenCalledWith(id, routePathSegments);
                expect(result).toEqual(
                    createComponentsState(
                        createComponentState(FAILED, 'test-team', 6, data).toLiteral()
                    )
                );
                expect(updateComponentHelperSpy).toHaveBeenCalledWith(
                    createComponentState(FAILED, 'test-team', 6, data).toLiteral()
                );
            });
        });

        describe('|COMPONENT_LOADED|', () => {
            it('should verify invokes correct methods', () => {
                // Given
                const action = ComponentLoaded.of(createComponentState(LOADING, 'test-team', 11));
                getComponentHelperSpy
                    .and
                    .returnValue(createComponentState(IDLE, 'test-team', 7).toLiteral());
                getStateHelperSpy
                    .and
                    .returnValue(
                        createComponentsState(
                            createComponentState(LOADED, 'test-team', 11).toLiteral()
                        )
                    );

                // When
                const result = componentReducer(literalComponentsState, action);

                // Then
                expect(getComponentHelperSpy).toHaveBeenCalledWith(id, routePathSegments);
                expect(result).toEqual(
                    createComponentsState(
                        createComponentState(LOADED, 'test-team', 11).toLiteral()
                    )
                );
                expect(updateComponentHelperSpy).toHaveBeenCalledWith(
                    createComponentState(LOADED, 'test-team', 11).toLiteral()
                );
            });
        });

        describe('|COMPONENT_FAILED|', () => {
            it('should verify invokes correct methods (data from action)', () => {
                // Given
                const data = new Map<string, any>([['data', []], ['invokes', {}]]);
                const action = new ActionStub<ComponentState>(
                    COMPONENT_FAILED,
                    createComponentState(IDLE, 'test-team', 9, data)
                );
                getComponentHelperSpy
                    .and
                    .returnValue(createComponentState(LOADING).toLiteral());
                getStateHelperSpy
                    .and
                    .returnValue(
                        createComponentsState(
                            createComponentState(FAILED, 'test-team', 9, data).toLiteral()
                        )
                    );

                // When
                const result = componentReducer(literalComponentsState, action);

                // Then
                expect(getComponentHelperSpy).toHaveBeenCalledWith(id, routePathSegments);
                expect(result).toEqual(
                    createComponentsState(
                        createComponentState(FAILED, 'test-team', 9, data).toLiteral()
                    )
                );
                expect(updateComponentHelperSpy).toHaveBeenCalledWith(
                    createComponentState(FAILED, 'test-team', 9, data).toLiteral()
                );
            });

            it('should verify invokes correct methods (data from store)', () => {
                // Given
                const data = new Map<string, any>([['wifi', []], ['routers', {}]]);
                const action = new ActionStub<ComponentState>(
                    COMPONENT_FAILED,
                    createComponentState(LOADING, 'test-team', 16)
                );
                getComponentHelperSpy
                    .and
                    .returnValue(createComponentState(LOADING, 'test-team', 14, data).toLiteral());
                getStateHelperSpy
                    .and
                    .returnValue(
                        createComponentsState(
                            createComponentState(FAILED, 'test-team', 16, data).toLiteral()
                        )
                    );

                // When
                const result = componentReducer(literalComponentsState, action);

                // Then
                expect(getComponentHelperSpy).toHaveBeenCalledWith(id, routePathSegments);
                expect(result).toEqual(
                    createComponentsState(
                        createComponentState(FAILED, 'test-team', 16, data).toLiteral()
                    )
                );
                expect(updateComponentHelperSpy).toHaveBeenCalledWith(
                    createComponentState(FAILED, 'test-team', 16, data).toLiteral()
                );
            });
        });

        describe('|COMPONENT_CLEAR_DATA|', () => {
            it('should verify invokes correct methods', () => {
                // Given
                const data = new Map<string, any>([['admins', []], ['telcos', {}]]);
                const action = new ActionStub<ComponentState>(
                    COMPONENT_CLEAR_DATA,
                    createComponentState(LOADED, 'test-team', 21)
                );
                getComponentHelperSpy
                    .and
                    .returnValue(createComponentState(LOADED, 'test-team', 15, data).toLiteral());
                getStateHelperSpy
                    .and
                    .returnValue(
                        createComponentsState(
                            createComponentState(LOADING, 'test-team', 21).toLiteral()
                        )
                    );

                // When
                const result = componentReducer(literalComponentsState, action);

                // Then
                expect(getComponentHelperSpy).toHaveBeenCalledWith(id, routePathSegments);
                expect(result).toEqual(
                    createComponentsState(
                        createComponentState(LOADING, 'test-team', 21).toLiteral()
                    )
                );
                expect(updateComponentHelperSpy).toHaveBeenCalledWith(
                    createComponentState(LOADING, 'test-team', 21).toLiteral()
                );
            });
        });

        describe('|ROUTER_NAVIGATION|', () => {
            it('should verify invokes correct methods', () => {
                // Given
                const routerNavigationPayload = createRouterNavigationPayload();
                const action = new ActionStub<RouterNavigationPayload<RouteState>>(
                    ROUTER_NAVIGATION,
                    routerNavigationPayload
                );
                const resetComponentsHelperSpy = spyOn(ComponentsStateHelper.prototype, 'resetComponentStates').and.callFake(CallFake);
                getStateHelperSpy
                    .and
                    .returnValue(
                        createComponentsState(
                            createComponentState(IDLE, 'test-team', 17).toLiteral()
                        )
                    );

                // When
                const result = componentReducer(literalComponentsState, action);

                // Then
                expect(resetComponentsHelperSpy).toHaveBeenCalledWith(routerNavigationPayload.routerState.routePathSegments);
                expect(result).toEqual(
                    createComponentsState(
                        createComponentState(IDLE, 'test-team', 17).toLiteral()
                    )
                );
            });
        });

        describe('|UNKNOWN_ACTION for this Reducer|', () => {
            it('should verify will return state as it is', () => {
                // Given
                const action = new ActionStub<any>('[action] unknown type', {});

                // When
                const result = componentReducer(literalComponentsState, action);

                // Then
                expect(result).toBe(literalComponentsState);
            });
        });
    });
});

class ActionStub<T> extends BaseActionWithPayload<T> {
    constructor(type: string, payload: T) {
        super(type, payload);
    }
}

const createComponentState = (
    status: StatusType,
    search = '',
    navigationId = 3,
    data: Map<string, any> = new Map<string, any>()): ComponentState => {

    const literalComponentState: LiteralComponentState = {
        id: 'testComponent1',
        status,
        routePath: 'test_entity/15',
        routePathSegments: ['test_entity/15'],
        navigationId,
        search,
        data: CollectionsUtil.transformMapToObject(data)
    };

    return {
        ...literalComponentState as any,
        data,
        copy: CallFake,
        toLiteral: () => literalComponentState,
        toLiteralDeepClone: () => literalComponentState
    } as ComponentState;
};

const createComponentsState = (componentState: LiteralComponentState): LiteralComponentsState => {
    return {
        components: {},
        routePathSegments: {
            'test_entity/15': {
                components: {
                    testComponent1: componentState
                },
                routePathSegments: {}
            }
        }
    };
};

const createRouterNavigationPayload = (): RouterNavigationPayload<RouteState> => {
    return {
        routerState: RouteState.of(
            RouteSegments.of('entity/21'),
            'entity/21'
        ),
        event: null
    };
};
