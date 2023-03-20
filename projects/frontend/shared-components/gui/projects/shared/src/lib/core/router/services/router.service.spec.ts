/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/dot-notation */

import { TestBed } from '@angular/core/testing';

import { of } from 'rxjs';
import { delay } from 'rxjs/operators';

import { marbles } from 'rxjs-marbles/jasmine';

import { Store } from '@ngrx/store';

import { STORE_ROUTER, StoreState } from '../../ngrx';

import { RouterState, RouteState } from '../model';

import { RouterService, RouterServiceImpl } from './router.service';

describe('RouterService -> RouterServiceImpl', () => {
    let storeStub$: jasmine.SpyObj<Store<StoreState>>;
    let service: RouterService;

    beforeEach(() => {
        storeStub$ = jasmine.createSpyObj<Store<StoreState>>('store', ['select']);

        TestBed.configureTestingModule({
            providers: [
                { provide: Store, useValue: storeStub$ },
                { provide: RouterService, useClass: RouterServiceImpl }
            ]
        });

        service = TestBed.inject(RouterService);
    });

    it('should verify instance is created', () => {
        // Then
        expect(service).toBeDefined();
    });

    describe('Statics::', () => {
        describe('Methods::', () => {
            describe('|get|', () => {
                it('should verify will return RouterState', () => {
                    // When
                    const routerState = RouterService.get();

                    // Then
                    expect(routerState.state).toEqual(RouteState.empty());
                });
            });

            describe('|getState|', () => {
                it('should verify will return RouteState', () => {
                    // When
                    const routeState = RouterService.getState();

                    // Then
                    expect(routeState).toEqual(RouteState.empty());
                });
            });
        });
    });

    describe('Methods::', () => {
        describe('|get|', () => {
            it('should verify will select RouterState from Store', () => {
                // Given
                storeStub$.select.and.returnValue(of({ state: {}, navigationId: 5 } as RouterState));

                // When
                service.get();

                // Then
                expect(storeStub$.select.calls.mostRecent().args).toEqual([STORE_ROUTER]);
            });

            it(
                'should verify will return correct Observable state',
                marbles((m) => {
                    // Given
                    const storeStream$ = m.cold('----a---', {
                        a: {
                            state: RouteState.empty(),
                            navigationId: 7
                        } as RouterState
                    });
                    const expectedOutputStream$ = m.cold('----a---', {
                        a: {
                            state: RouteState.empty(),
                            navigationId: 7
                        } as RouterState
                    });
                    storeStub$.select.and.returnValue(storeStream$);

                    // When
                    const response$ = service.get();

                    // Then
                    m.expect(response$).toBeObservable(expectedOutputStream$);
                })
            );
        });

        describe('|getState|', () => {
            it('should verify will select RouterState from Store', () => {
                // Given
                storeStub$.select.and.returnValue(of({ state: {}, navigationId: 5 } as RouterState));

                // When
                service.getState();

                // Then
                expect(storeStub$.select.calls.mostRecent().args).toEqual([STORE_ROUTER]);
            });

            it(
                'should verify will return correct Observable state',
                marbles((m) => {
                    // Given
                    const storeStream$ = m.cold('----a---', {
                        a: {
                            state: RouteState.empty(),
                            navigationId: 7
                        } as RouterState
                    });
                    const expectedOutputStream$ = m.cold('----a---', {
                        a: RouteState.empty()
                    });
                    storeStub$.select.and.returnValue(storeStream$);

                    // When
                    const response$ = service.getState();

                    // Then
                    m.expect(response$).toBeObservable(expectedOutputStream$);
                })
            );
        });

        describe('|initialize|', () => {
            it('should verify will push created subscriptions to buffer', () => {
                // Given
                const storeStream$ = of({
                    state: RouteState.empty(),
                    navigationId: 7
                } as RouterState);
                storeStub$.select.and.returnValue(storeStream$);
                // @ts-ignore
                const cleanSubSpy = spyOn(service, 'cleanSubscriptions').and.callThrough();

                // Then 1
                expect(service['subscriptions'].length).toEqual(0);

                // When
                service.initialize();

                // Then 2
                expect(service['subscriptions'].length).toEqual(1);
                expect(cleanSubSpy).toHaveBeenCalled();
            });

            it(
                'should verify will create subscriptions and will assign value to local state',
                marbles((m) => {
                    // Given
                    const routerState = RouterState.of(RouteState.empty(), 7);
                    const storeStream$ = m.hot('-^--a---', {
                        a: routerState
                    });
                    storeStub$.select.and.returnValue(storeStream$);

                    // When 1
                    service.initialize();

                    // delay of 4 frames
                    of(true)
                        .pipe(delay(m.time('----|')))
                        .subscribe(() => {
                            // Then 1
                            expect(RouterService['_routerState']).toBe(routerState);

                            // When 2 // destroy Service
                            service.ngOnDestroy();

                            // Then
                            m.expect(storeStream$).toHaveSubscriptions('^---!');
                        });
                })
            );
        });
    });
});
