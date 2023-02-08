

import { throwError } from 'rxjs';

import { marbles } from 'rxjs-marbles/jasmine';

import { RouterState, RouteSegments, RouteState } from '../../../router';

import { BaseActionWithPayload } from '../../../ngrx';

import { ComponentModel, ComponentState, ComponentStateImpl, FAILED, INITIALIZED, LOADED } from '../../model';
import { ComponentService } from '../../services';

import { ComponentFailed } from '../actions';

import { getModel, getModelAndTask, handleActionError } from './component-rx.operators';
import { CollectionsUtil } from '../../../../utils';

describe('rxjs operators', () => {
    describe('|getModel|', () => {
        it('should verify will create ComponentModel down the stream', marbles((m) => {
            // Given
            const inputActionStream$ = m.cold('----a---b----', {
                a: new ActionStub(ComponentStateImpl.of({
                    id: 'test1',
                    status: INITIALIZED,
                    routePathSegments: ['entity/10']
                })),
                b: new ActionStub(ComponentStateImpl.of({
                    id: 'test2', status: LOADED,
                    routePathSegments: ['entity/225']
                }))
            });
            const getModelStream1$ = m.cold('-a', {
                a: ComponentModel.of(
                    ComponentStateImpl.of({ id: 'test1', status: INITIALIZED }),
                    RouterState.of(
                        RouteState.of(
                            RouteSegments.of('entity/10'),
                            'entity/5'
                        ),
                        3
                    )
                )
            });
            const getModelStream2$ = m.cold('--a', {
                a: ComponentModel.of(
                    ComponentStateImpl.of({ id: 'test5', status: LOADED }),
                    RouterState.of(
                        RouteState.of(
                            RouteSegments.of('entity/225'),
                            'entity/225'
                        ),
                        3
                    )
                )
            });
            const expectedOutputStream$ = m.cold('-----a----b----', {
                a: ComponentModel.of(
                    ComponentStateImpl.of({ id: 'test1', status: INITIALIZED }),
                    RouterState.of(
                        RouteState.of(
                            RouteSegments.of('entity/10'),
                            'entity/5'
                        ),
                        3
                    )
                ),
                b: ComponentModel.of(
                    ComponentStateImpl.of({ id: 'test5', status: LOADED }),
                    RouterState.of(
                        RouteState.of(
                            RouteSegments.of('entity/225'),
                            'entity/225'
                        ),
                        3
                    )
                )
            });

            const componentServiceStub = jasmine.createSpyObj<ComponentService>('componentService', ['getModel']);
            let cnt = 0;
            componentServiceStub.getModel.and.callFake(() => {
                cnt++;
                if (cnt === 1) {
                    return getModelStream1$;
                } else {
                    return getModelStream2$;
                }
            });

            // When
            const response$ = getModel(componentServiceStub)(inputActionStream$);

            // Then
            m.expect(response$).toBeObservable(expectedOutputStream$);
        }));
    });

    describe('|getModelAndTask|', () => {
        it('should verify will create ComponentModel down the stream', marbles((m) => {
            // Given
            const taskIdentifier1 = `patch_entity __ ${ new Date().toISOString() }`;
            const taskIdentifier2 = `patch_dataset __ ${ new Date().toISOString() }`;
            spyOn(CollectionsUtil, 'interpolateString').and.returnValues(taskIdentifier1, taskIdentifier2);
            const inputActionStream$ = m.cold('----a---b----', {
                a: new ActionStub(
                    ComponentStateImpl.of({
                        id: 'test1',
                        status: INITIALIZED,
                        routePathSegments: ['entity/10']
                    }),
                    taskIdentifier1
                ),
                b: new ActionStub(
                    ComponentStateImpl.of({
                        id: 'test2', status: LOADED,
                        routePathSegments: ['entity/225']
                    }),
                    taskIdentifier2
                )
            });
            const getModelStream1$ = m.cold('-a', {
                a: ComponentModel.of(
                    ComponentStateImpl.of({ id: 'test1', status: INITIALIZED }),
                    RouterState.of(
                        RouteState.of(
                            RouteSegments.of('entity/10'),
                            'entity/5'
                        ),
                        3
                    )
                )
            });
            const getModelStream2$ = m.cold('--a', {
                a: ComponentModel.of(
                    ComponentStateImpl.of({ id: 'test5', status: LOADED }),
                    RouterState.of(
                        RouteState.of(
                            RouteSegments.of('entity/225'),
                            'entity/225'
                        ),
                        3
                    )
                )
            });
            const expectedOutputStream$ = m.cold('-----a----b----', {
                a: [
                    ComponentModel.of(
                        ComponentStateImpl.of({ id: 'test1', status: INITIALIZED }),
                        RouterState.of(
                            RouteState.of(
                                RouteSegments.of('entity/10'),
                                'entity/5'
                            ),
                            3
                        )
                    ),
                    taskIdentifier1
                ] as [ComponentModel, string],
                b: [
                    ComponentModel.of(
                        ComponentStateImpl.of({ id: 'test5', status: LOADED }),
                        RouterState.of(
                            RouteState.of(
                                RouteSegments.of('entity/225'),
                                'entity/225'
                            ),
                            3
                        )
                    ),
                    taskIdentifier2
                ] as [ComponentModel, string]
            });

            const componentServiceStub = jasmine.createSpyObj<ComponentService>('componentService', ['getModel']);
            let cnt = 0;
            componentServiceStub.getModel.and.callFake(() => {
                cnt++;
                if (cnt === 1) {
                    return getModelStream1$;
                } else {
                    return getModelStream2$;
                }
            });

            // When
            const response$ = getModelAndTask(componentServiceStub)(inputActionStream$);

            // Then
            m.expect(response$).toBeObservable(expectedOutputStream$);
        }));
    });

    describe('|handleActionError|', () => {
        it('should verify will handle Stream error and return ComponentFailed action', marbles((m) => {
            // Given
            const inputModel = ComponentModel.of(
                ComponentStateImpl.of({ id: 'test1', status: INITIALIZED, navigationId: 3 }),
                RouterState.of(
                    RouteState.of(
                        RouteSegments.of('entity/10'),
                        'entity/5'
                    ),
                    3
                )
            );
            const error = new Error('Http Failure');
            const getResponseStream$ = throwError(error);
            const expectedOutputStream$ = m.cold('(a|)', {
                a: ComponentFailed.of(
                    ComponentStateImpl.of({ id: 'test1', status: FAILED, navigationId: 3, error })
                )
            });

            // When
            const response$ = handleActionError(inputModel)(getResponseStream$);

            // Then
            m.expect(response$).toBeObservable(expectedOutputStream$);
        }));
    });
});

class ActionStub extends BaseActionWithPayload<ComponentState> {
    constructor(payload: ComponentState, task?: string) {
        super('[component] action stub', payload, task);
    }
}
