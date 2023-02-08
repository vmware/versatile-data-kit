

/* eslint-disable @typescript-eslint/dot-notation,arrow-body-style,prefer-arrow/prefer-arrow-functions */

import { TestBed } from '@angular/core/testing';

import { Store } from '@ngrx/store';
import { RouterReducerState } from '@ngrx/router-store';

import { of, throwError } from 'rxjs';

import { marbles } from 'rxjs-marbles/jasmine';

import { CollectionsUtil } from '../../../utils';

import { GenericAction, STORE_COMPONENTS, STORE_ROUTER, StoreState } from '../../ngrx';
import { RouterService, RouterState, RouteSegments, RouteState } from '../../router';

import {
    ComponentModel,
    ComponentState,
    ComponentStateImpl,
    FAILED,
    IDLE,
    INITIALIZED,
    LiteralComponentsState,
    LiteralComponentState,
    LOADED,
    LOADING,
    StatusType
} from '../model';
import { ComponentIdle, ComponentInit, ComponentLoading, ComponentUpdate } from '../state';

import { ComponentService, ComponentServiceImpl } from './component.service';

describe('ComponentService -> ComponentServiceImpl', () => {
    let storeStub$: jasmine.SpyObj<Store<StoreState>>;
    let routerServiceStub: jasmine.SpyObj<RouterService>;

    let service: ComponentService;

    beforeEach(() => {
        storeStub$ = jasmine.createSpyObj<Store<StoreState>>('store', ['select', 'dispatch']);
        routerServiceStub = jasmine.createSpyObj<RouterService>('routerService', ['get', 'getState']);

        TestBed.configureTestingModule({
            providers: [
                { provide: Store, useValue: storeStub$ },
                { provide: RouterService, useValue: routerServiceStub },
                { provide: ComponentService, useClass: ComponentServiceImpl }
            ]
        });

        service = TestBed.inject(ComponentService);
    });

    it('should verify service is created', () => {
        // Then
        expect(service).toBeDefined();
    });

    describe('Methods::', () => {
        let id: string;
        let components: LiteralComponentsState;
        let router: RouterState;

        beforeEach(() => {
            id = 'testComponent10';
            router = createStoreState()[STORE_ROUTER];

            routerServiceStub.getState.and.returnValue(of(router.state));
            routerServiceStub.get.and.returnValue(of(router));
        });

        describe('|init|', () => {
            it('should verify will initialize correct component and dispatch ComponentInit', () => {
                // Given
                const componentState = createComponentState(router, id, INITIALIZED);

                storeStub$.select.and.callFake((param) => {
                    if (param === STORE_COMPONENTS) {
                        components = createStoreState(componentState.toLiteral())[STORE_COMPONENTS];

                        return of(components);
                    }

                    return of(createStoreState());
                });

                // When
                const response$ = service.init(id, router.state);

                // Then
                expect(storeStub$.select.calls.argsFor(0)).toEqual([jasmine.any(Function)]);
                expect(storeStub$.select.calls.argsFor(1)).toEqual([STORE_COMPONENTS]);
                expect(storeStub$.dispatch).toHaveBeenCalledWith(ComponentInit.of(componentState));

                response$.subscribe((model) => {
                    expect(model['_routerState']).toEqual(router);
                    expect(model['_componentState']).toEqual(getComponentState(components, id));
                    expect(model.status).toEqual(INITIALIZED);
                });

                expect(routerServiceStub.getState).toHaveBeenCalled();
                expect(storeStub$.select.calls.argsFor(2)).toEqual([STORE_COMPONENTS]);
                expect(routerServiceStub.get).toHaveBeenCalled();
            }, 1000);

            it('should verify wont dispatch ComponentInit', () => {
                // Given
                const componentState = createComponentState(router, id, LOADED);

                storeStub$.select.and.callFake((param) => {
                    if (param === STORE_COMPONENTS) {
                        components = createStoreState(componentState.toLiteral())[STORE_COMPONENTS];

                        return of(components);
                    }

                    return of(createStoreState(componentState.toLiteral()));
                });

                // When
                const response$ = service.init(id, router.state);

                // Then
                expect(storeStub$.select.calls.argsFor(0)).toEqual([jasmine.any(Function)]);
                expect(storeStub$.dispatch).not.toHaveBeenCalled();
                expect(storeStub$.select.calls.argsFor(1)).toEqual([STORE_COMPONENTS]);

                response$.subscribe((model) => {
                    expect(model['_routerState']).toEqual(router);
                    expect(model['_componentState']).toEqual(getComponentState(components, id));
                    expect(model.status).toEqual(LOADED);
                });

                expect(routerServiceStub.getState).toHaveBeenCalled();
                expect(storeStub$.select.calls.argsFor(2)).toEqual([STORE_COMPONENTS]);
                expect(routerServiceStub.get).toHaveBeenCalled();
            }, 1000);
        });

        describe('|idle|', () => {
            it('should verify will dispatch ComponentIdle with provided ComponentState', () => {
                // Given
                const componentState = createComponentState(router, id, LOADED);

                // When
                service.idle(componentState);

                // Then
                expect(storeStub$.dispatch).toHaveBeenCalledWith(ComponentIdle.of(componentState));
            });
        });

        describe('|load|', () => {
            it('should verify will dispatch ComponentLoading with provided ComponentState', () => {
                // Given
                const componentState = createComponentState(router, id, FAILED);
                routerServiceStub.get.and.returnValue(of(router));
                storeStub$.select
                          .and
                          .returnValue(
                              of(createStoreState(createComponentState(router, id, LOADED).toLiteral())[STORE_COMPONENTS])
                          );

                // When
                const response$ = service.load(componentState);

                // Then
                expect(routerServiceStub.get).toHaveBeenCalledTimes(1);
                // @ts-ignore
                expect(storeStub$.dispatch.calls.argsFor(0)).toEqual([
                    ComponentLoading.of(
                        componentState.copy({
                            navigationId: router.navigationId,
                            status: LOADING
                        })
                    )
                ]);

                const assertionComponentState = createComponentState(router, id, LOADED);
                response$.subscribe((model) => {
                    expect(model['_routerState']).toEqual(router);
                    expect(model['_componentState']).toEqual(assertionComponentState);
                    expect(model.status).toEqual(LOADED);
                });

                // @ts-ignore
                expect(storeStub$.select).toHaveBeenCalledWith(STORE_COMPONENTS);
                expect(routerServiceStub.getState).toHaveBeenCalled();
                expect(routerServiceStub.get).toHaveBeenCalledTimes(2);
            }, 1000);

            it('should verify will dispatch ComponentIdle and ComponentLoading with provided component id', () => {
                // Given
                const componentState = createComponentState(router, id, INITIALIZED);
                routerServiceStub.get.and.returnValue(of(router));
                storeStub$.select
                          .and
                          .returnValue(
                              of(createStoreState(createComponentState(router, id, LOADED).toLiteral())[STORE_COMPONENTS])
                          );

                // When
                const response$ = service.load(componentState);

                // Then
                expect(routerServiceStub.get).toHaveBeenCalledTimes(1);
                // @ts-ignore
                expect(storeStub$.dispatch.calls.argsFor(0)).toEqual([
                    ComponentIdle.of(
                        createComponentState(router, id, IDLE).copy({
                            navigationId: router.navigationId
                        })
                    )
                ]);
                expect(storeStub$.dispatch.calls.argsFor(1)).toEqual([
                    ComponentLoading.of(
                        createComponentState(router, id, LOADING).copy({
                            navigationId: router.navigationId
                        })
                    )
                ]);

                const assertionComponentState = createComponentState(router, id, LOADED);
                response$.subscribe((model) => {
                    expect(model['_routerState']).toEqual(router);
                    expect(model['_componentState']).toEqual(assertionComponentState);
                    expect(model.status).toEqual(LOADED);
                });

                // @ts-ignore
                expect(storeStub$.select).toHaveBeenCalledWith(STORE_COMPONENTS);
                expect(routerServiceStub.getState).toHaveBeenCalled();
                expect(routerServiceStub.get).toHaveBeenCalledTimes(2);
            }, 1000);
        });

        describe('|update|', () => {
            it('should verify will dispatch ComponentUpdate with provided ComponentState', () => {
                // Given
                const componentState = createComponentState(router, id, LOADED);

                // When
                service.update(componentState);

                // Then
                expect(routerServiceStub.get).toHaveBeenCalled();
                expect(storeStub$.dispatch).toHaveBeenCalledWith(
                    ComponentUpdate.of(
                        componentState.copy({ navigationId: router.navigationId })
                    )
                );
            });
        });

        describe('|hasInSegment|', () => {
            it('should verify will return true when ComponentState exist', marbles((m) => {
                // Given
                const componentsStream$ = m.cold('---a', {
                    a: createStoreState(
                        createComponentState(router, 'someComponentId', LOADED).toLiteral())[STORE_COMPONENTS]
                });
                const routeStateStream$ = m.cold('--a', {
                    a: router.state
                });
                storeStub$.select.and.returnValue(componentsStream$);
                routerServiceStub.getState.and.returnValue(routeStateStream$);
                const expected$ = m.cold('---(a|)', { a: true });

                // When
                const response$ = service.hasInSegment('someComponentId', ['test_domain/context', 'test_entity/10']);

                // Then
                m.expect(response$).toBeObservable(expected$);
            }));

            it('should verify will return false when ComponentState not exist', marbles((m) => {
                // Given
                const componentsStream$ = m.cold('---a', {
                    a: createStoreState(
                        createComponentState(router, 'someComponentId', LOADED).toLiteral())[STORE_COMPONENTS]
                });
                const routeStateStream$ = m.cold('---a', {
                    a: router.state
                });
                storeStub$.select.and.returnValue(componentsStream$);
                routerServiceStub.getState.and.returnValue(routeStateStream$);
                const expected$ = m.cold('---(a|)', { a: false });

                // When
                const response$ = service.hasInSegment('newComponentId', ['test_domain/context', 'test_entity/10']);

                // Then
                m.expect(response$).toBeObservable(expected$);
            }));
        });

        describe('|onInit|', () => {
            it(`should verify wont emit when state doesn't exist`, marbles((m) => {
                // Given
                const cA = createStoreState(createComponentState(router, 'testId10', INITIALIZED).toLiteral());
                const cB = createStoreState(createComponentState(router, 'testId10', IDLE).toLiteral());
                const cC = createStoreState(createComponentState(router, 'testId10', LOADING).toLiteral());
                const cD = createStoreState(createComponentState(router, 'testId10', LOADED).toLiteral());
                const cE = createStoreState(createComponentState(router, 'testId22', LOADED).toLiteral());
                const cF = createStoreState(createComponentState(router, 'testId33', LOADED).toLiteral());
                const componentsMarbleStream$ = m.cold('-a--bc-d-e--f-|', {
                    a: cA[STORE_COMPONENTS],
                    b: cB[STORE_COMPONENTS],
                    c: cC[STORE_COMPONENTS],
                    d: cD[STORE_COMPONENTS],
                    e: cE[STORE_COMPONENTS],
                    f: cF[STORE_COMPONENTS]
                });
                const expectedModelMarbleStream$ = m.cold('--------------|');
                storeStub$.select.and.returnValue(componentsMarbleStream$);

                // When
                const response$ = service.onInit(id, router.state.routePathSegments);

                // Then
                m.expect(response$).toBeObservable(expectedModelMarbleStream$);
            }));

            it('should verify will emit when state exist', () => {
                // Given
                const componentState = createComponentState(router, id, INITIALIZED);
                const storeState = createStoreState(componentState.toLiteral());

                storeStub$.select.and.returnValue(of(storeState[STORE_COMPONENTS]));

                // When
                const response$ = service.onInit(id, router.state.routePathSegments);

                // Then
                // @ts-ignore
                expect(storeStub$.select.calls.argsFor(0)).toEqual([STORE_COMPONENTS]);
                expect(routerServiceStub.getState).toHaveBeenCalled();

                response$.subscribe((model) => {
                    expect(model).toBeDefined();
                    expect(model.status).toEqual(INITIALIZED);
                });

                expect(storeStub$.select.calls.argsFor(1)).toEqual([STORE_COMPONENTS]);
                expect(routerServiceStub.get).toHaveBeenCalled();
            }, 1000);
        });

        describe('|onLoaded|', () => {
            it(`should verify wont emit when state doesn't exist`, marbles((m) => {
                // Given
                const cA = createStoreState(createComponentState(router, 'testId1', INITIALIZED).toLiteral());
                const cB = createStoreState(createComponentState(router, 'testId1', IDLE).toLiteral());
                const cC = createStoreState(createComponentState(router, 'testId1', LOADING).toLiteral());
                const cD = createStoreState(createComponentState(router, 'testId1', LOADED).toLiteral());
                const cE = createStoreState(createComponentState(router, 'testId2', LOADED).toLiteral());
                const cF = createStoreState(createComponentState(router, 'testId3', LOADED).toLiteral());
                const componentsMarbleStream$ = m.cold('-a--bc---d--e----f-|', {
                    a: cA[STORE_COMPONENTS],
                    b: cB[STORE_COMPONENTS],
                    c: cC[STORE_COMPONENTS],
                    d: cD[STORE_COMPONENTS],
                    e: cE[STORE_COMPONENTS],
                    f: cF[STORE_COMPONENTS]
                });
                const expectedModelMarbleStream$ = m.cold('-------------------|');
                storeStub$.select.and.returnValue(componentsMarbleStream$);

                // When
                const response$ = service.onLoaded(id, router.state.routePathSegments);

                // Then
                m.expect(response$).toBeObservable(expectedModelMarbleStream$);
            }));

            it('should verify wont emit when state status is not LOADED or FAILED', marbles((m) => {
                // Given
                const cA = createStoreState(createComponentState(router, id, INITIALIZED).toLiteral());
                const cB = createStoreState(createComponentState(router, id, IDLE).toLiteral());
                const cC = createStoreState(createComponentState(router, id, LOADING).toLiteral());
                const componentsMarbleStream$ = m.cold('-a--bc---|', {
                    a: cA[STORE_COMPONENTS],
                    b: cB[STORE_COMPONENTS],
                    c: cC[STORE_COMPONENTS]
                });
                const expectedModelMarbleStream$ = m.cold('---------|');
                storeStub$.select.and.returnValue(componentsMarbleStream$);

                // When
                const response$ = service.onLoaded(id, router.state.routePathSegments);

                // Then
                m.expect(response$).toBeObservable(expectedModelMarbleStream$);
            }));

            it('should verify will emit when state exist and its status is LOADED', marbles((m) => {
                // Given
                const cA = createStoreState(createComponentState(router, id, INITIALIZED).toLiteral());
                const cB = createStoreState(createComponentState(router, id, IDLE).toLiteral());
                const cC = createStoreState(createComponentState(router, id, LOADING).toLiteral());
                const cD = createStoreState(createComponentState(router, id, LOADED).toLiteral());
                const componentsMarbleStream$ = m.cold('-a--bc---d---', {
                    a: cA[STORE_COMPONENTS],
                    b: cB[STORE_COMPONENTS],
                    c: cC[STORE_COMPONENTS],
                    d: cD[STORE_COMPONENTS]
                });
                const componentsMarbleStream1$ = m.cold('d----', {
                    d: cD[STORE_COMPONENTS]
                });
                const expectedModelMarbleStream$ = m.cold('---------(a|)', {
                    a: ComponentModel.of(getComponentState(cD, id), cD[STORE_ROUTER])
                });
                let cnt = 0;
                storeStub$.select.and.callFake(() => {
                    cnt++;
                    if (cnt === 1) {
                        return componentsMarbleStream$;
                    }

                    if (cnt === 2) {
                        return componentsMarbleStream1$;
                    }

                    return throwError(() => new Error(`This shouldn't be reachable`));
                });
                routerServiceStub.getState.and.returnValue(m.cold('a----', { a: router.state }));
                routerServiceStub.get.and.returnValue(m.cold('a----', { a: router }));

                // When
                const response$ = service.onLoaded(id, router.state.routePathSegments);

                // Then
                m.expect(response$).toBeObservable(expectedModelMarbleStream$);
            }));

            it('should verify will emit when state exist and its status is FAILED', marbles((m) => {
                // Given
                const cA = createStoreState(createComponentState(router, id, INITIALIZED).toLiteral());
                const cB = createStoreState(createComponentState(router, id, IDLE).toLiteral());
                const cC = createStoreState(createComponentState(router, id, LOADING).toLiteral());
                const cD = createStoreState(createComponentState(router, id, FAILED).toLiteral());
                const componentsMarbleStream$ = m.cold('-a--bc---d---', {
                    a: cA[STORE_COMPONENTS],
                    b: cB[STORE_COMPONENTS],
                    c: cC[STORE_COMPONENTS],
                    d: cD[STORE_COMPONENTS]
                });
                const componentsMarbleStream1$ = m.cold('d----', {
                    d: cD[STORE_COMPONENTS]
                });
                const expectedModelMarbleStream$ = m.cold('---------(a|)', {
                    a: ComponentModel.of(getComponentState(cD, id), cD[STORE_ROUTER])
                });
                let cnt = 0;
                storeStub$.select.and.callFake(() => {
                    cnt++;
                    if (cnt === 1) {
                        return componentsMarbleStream$;
                    }

                    if (cnt === 2) {
                        return componentsMarbleStream1$;
                    }

                    return throwError(() => new Error(`This shouldn't be reachable`));
                });
                routerServiceStub.getState.and.returnValue(m.cold('a----', { a: router.state }));
                routerServiceStub.get.and.returnValue(m.cold('a----', { a: router }));

                // When
                const response$ = service.onLoaded(id, router.state.routePathSegments);

                // Then
                m.expect(response$).toBeObservable(expectedModelMarbleStream$);
            }));
        });

        describe('|getModel|', () => {
            it(`should verify wont emit when state doesn't exist`, marbles((m) => {
                // Given
                const cA = createStoreState(createComponentState(router, 'testId21', INITIALIZED).toLiteral());
                const cB = createStoreState(createComponentState(router, 'testId21', IDLE).toLiteral());
                const cC = createStoreState(createComponentState(router, 'testId21', LOADING).toLiteral());
                const cD = createStoreState(createComponentState(router, 'testId21', LOADED).toLiteral());
                const cE = createStoreState(createComponentState(router, 'testId32', LOADED).toLiteral());
                const cF = createStoreState(createComponentState(router, 'testId33', LOADED).toLiteral());
                const componentsMarbleStream$ = m.cold('--a-bc---d----e--f---|', {
                    a: cA[STORE_COMPONENTS],
                    b: cB[STORE_COMPONENTS],
                    c: cC[STORE_COMPONENTS],
                    d: cD[STORE_COMPONENTS],
                    e: cE[STORE_COMPONENTS],
                    f: cF[STORE_COMPONENTS]
                });
                const expectedModelMarbleStream$ = m.cold('---------------------|');
                storeStub$.select.and.returnValue(componentsMarbleStream$);

                // When
                const response$ = service.getModel(id, router.state.routePathSegments);

                // Then
                m.expect(response$).toBeObservable(expectedModelMarbleStream$);
            }));

            it('should verify will emit on every status', marbles((m) => {
                // Given
                const cA = createStoreState(createComponentState(router, id, INITIALIZED).toLiteral());
                const cB = createStoreState(createComponentState(router, id, IDLE).toLiteral());
                const cC = createStoreState(createComponentState(router, id, LOADING).toLiteral());
                const cD = createStoreState(createComponentState(router, id, LOADED).toLiteral());
                const cE = createStoreState(createComponentState(router, id, FAILED).toLiteral());
                const componentsMarbleStream$ = m.cold('-a--bc---d---e-', {
                    a: cA[STORE_COMPONENTS],
                    b: cB[STORE_COMPONENTS],
                    c: cC[STORE_COMPONENTS],
                    d: cD[STORE_COMPONENTS],
                    e: cE[STORE_COMPONENTS]
                });
                const expectedModelMarbleStream$ = m.cold('-a--bc---d---e-', {
                    a: ComponentModel.of(getComponentState(cA, id), cA[STORE_ROUTER]),
                    b: ComponentModel.of(getComponentState(cB, id), cB[STORE_ROUTER]),
                    c: ComponentModel.of(getComponentState(cC, id), cC[STORE_ROUTER]),
                    d: ComponentModel.of(getComponentState(cD, id), cD[STORE_ROUTER]),
                    e: ComponentModel.of(getComponentState(cE, id), cE[STORE_ROUTER])
                });
                storeStub$.select.and.returnValue(componentsMarbleStream$);
                routerServiceStub.get.and.returnValue(m.cold('a', { a: router }));

                // When
                const response$ = service.getModel(id, router.state.routePathSegments, ['*']);

                // Then
                m.expect(response$).toBeObservable(expectedModelMarbleStream$);
            }));

            it('should verify will emit on requested statuses', marbles((m) => {
                // Given
                const cA = createStoreState(createComponentState(router, id, INITIALIZED).toLiteral());
                const cB = createStoreState(createComponentState(router, id, IDLE).toLiteral());
                const cC = createStoreState(createComponentState(router, id, LOADING).toLiteral());
                const cD = createStoreState(createComponentState(router, id, LOADED).toLiteral());
                const cE = createStoreState(createComponentState(router, id, FAILED).toLiteral());
                const componentsMarbleStream$ = m.cold('-a--bc---d---e-', {
                    a: cA[STORE_COMPONENTS],
                    b: cB[STORE_COMPONENTS],
                    c: cC[STORE_COMPONENTS],
                    d: cD[STORE_COMPONENTS],
                    e: cE[STORE_COMPONENTS]
                });
                const expectedModelMarbleStream$ = m.cold('-----c-------e-', {
                    c: ComponentModel.of(getComponentState(cC, id), cC[STORE_ROUTER]),
                    e: ComponentModel.of(getComponentState(cE, id), cE[STORE_ROUTER])
                });
                storeStub$.select.and.returnValue(componentsMarbleStream$);
                routerServiceStub.get.and.returnValue(m.cold('a', { a: router }));

                // When
                const response$ = service.getModel(id, router.state.routePathSegments, [LOADING, FAILED]);

                // Then
                m.expect(response$).toBeObservable(expectedModelMarbleStream$);
            }));

            it('should verify will emit on default statuses', marbles((m) => {
                // Given
                const cA = createStoreState(createComponentState(router, id, INITIALIZED).toLiteral());
                const cB = createStoreState(createComponentState(router, id, IDLE).toLiteral());
                const cC = createStoreState(createComponentState(router, id, LOADING).toLiteral());
                const cD = createStoreState(createComponentState(router, id, LOADED).toLiteral());
                const cE = createStoreState(createComponentState(router, id, LOADING).toLiteral());
                const cF = createStoreState(createComponentState(router, id, FAILED).toLiteral());
                const componentsMarbleStream$ = m.cold('-a--bc---d---e---f-', {
                    a: cA[STORE_COMPONENTS],
                    b: cB[STORE_COMPONENTS],
                    c: cC[STORE_COMPONENTS],
                    d: cD[STORE_COMPONENTS],
                    e: cE[STORE_COMPONENTS],
                    f: cF[STORE_COMPONENTS]
                });
                const expectedModelMarbleStream$ = m.cold('---------d-------f-', {
                    d: ComponentModel.of(getComponentState(cD, id), cD[STORE_ROUTER]),
                    f: ComponentModel.of(getComponentState(cF, id), cF[STORE_ROUTER])
                });
                storeStub$.select.and.returnValue(componentsMarbleStream$);
                routerServiceStub.get.and.returnValue(m.cold('a', { a: router }));

                // When
                const response$ = service.getModel(id, router.state.routePathSegments);

                // Then
                m.expect(response$).toBeObservable(expectedModelMarbleStream$);
            }));
        });

        describe('|dispatchAction|', () => {
            it('should verify will invoke correct methods', () => {
                // Given
                const componentState = createComponentState(router, id, LOADING);
                const typeStub = '[component] Some Action';
                const modelStub = {
                    getComponentState: () => componentState
                } as ComponentModel;
                const getModelSpy = spyOn(service, 'getModel').and.returnValue(of(modelStub));
                const actionStub = { type: typeStub, payload: componentState, task: undefined };
                const genericActionOfSpy = spyOn(GenericAction, 'of').and.returnValue(actionStub);

                // When
                service.dispatchAction(typeStub, componentState);

                // Then
                expect(getModelSpy).toHaveBeenCalledWith(componentState.id, componentState.routePathSegments, ['*']);
                expect(genericActionOfSpy).toHaveBeenCalledWith(typeStub, componentState, undefined);
                expect(storeStub$.dispatch).toHaveBeenCalledWith(actionStub);
            });

            it('should verify will invoke correct methods when Task is provided', () => {
                // Given
                const taskIdentifier = `search_data __ ${ new Date().toISOString() }`;
                const componentState = createComponentState(router, id, INITIALIZED);
                const typeStub = '[component] Load Users';
                const modelStub = {
                    getComponentState: () => componentState
                } as ComponentModel;
                const getModelSpy = spyOn(service, 'getModel').and.returnValue(of(modelStub));
                const actionStub = {
                    type: typeStub,
                    payload: componentState,
                    task: taskIdentifier
                };
                const genericActionOfSpy = spyOn(GenericAction, 'of').and.returnValue(actionStub);

                // When
                service.dispatchAction(typeStub, componentState, taskIdentifier);

                // Then
                expect(getModelSpy).toHaveBeenCalledWith(componentState.id, componentState.routePathSegments, ['*']);
                expect(genericActionOfSpy).toHaveBeenCalledWith(typeStub, componentState, taskIdentifier);
                expect(storeStub$.dispatch).toHaveBeenCalledWith(actionStub);
            });
        });
    });
});

const createComponentState = (router: RouterReducerState<RouteState>, id: string, status: StatusType) => {
    return ComponentStateImpl.of({
        id,
        status,
        routePath: router?.state.routePath ?? null,
        routePathSegments: router?.state.routePathSegments ?? [],
        navigationId: router.navigationId
    });
};

const getComponentState = (state: StoreState | LiteralComponentsState, id: string): ComponentState => {
    if (CollectionsUtil.isNil(state)) {
        return ComponentStateImpl.of({});
    }

    const componentsState = (
        CollectionsUtil.isNil((state as LiteralComponentsState).routePathSegments)
            ? state[STORE_COMPONENTS]
            : state
    ) as LiteralComponentsState;

    return ComponentStateImpl.fromLiteralComponentState(
        componentsState
            .routePathSegments['test_domain/context']
            .routePathSegments['test_entity/10']
            .components[id]
    );
};

const createStoreState = (state?: LiteralComponentState): StoreState => {
    return CollectionsUtil.isNil(state)
        ? {
            [STORE_ROUTER]: RouterState.of(
                RouteState.of(
                    RouteSegments.of(
                        'test_entity/10',
                        {},
                        { entity: 10 },
                        null,
                        RouteSegments.of('test_domain/context')
                    ),
                    '/domain/context/entity/10'
                ),
                3
            ),
            [STORE_COMPONENTS]: {
                components: {},
                routePathSegments: {}
            }
        }
        : {
            [STORE_ROUTER]: RouterState.of(
                RouteState.of(
                    RouteSegments.of(
                        'test_entity/10',
                        {},
                        { entity: 10 },
                        null,
                        RouteSegments.of('test_domain/context')
                    ),
                    '/domain/context/entity/10'
                ),
                3
            ),
            [STORE_COMPONENTS]: {
                components: {},
                routePathSegments: {
                    'test_domain/context': {
                        components: {},
                        routePathSegments: {
                            'test_entity/10': {
                                components: {
                                    [state.id]: state
                                },
                                routePathSegments: {}
                            }
                        }
                    }
                }
            }
        };
};
