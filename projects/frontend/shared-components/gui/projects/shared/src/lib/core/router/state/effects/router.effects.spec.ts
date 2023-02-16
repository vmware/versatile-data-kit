

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Location } from '@angular/common';
import { Router } from '@angular/router';
import { TestBed, waitForAsync } from '@angular/core/testing';

import { provideMockActions } from '@ngrx/effects/testing';

import { Observable } from 'rxjs';
import { marbles } from 'rxjs-marbles/jasmine';

import { RouterEffects } from './router.effects';
import { LocationBack, LocationForward, LocationGo, RouterNavigate } from '../actions';

describe('RouterEffects', () => {
    let effects: RouterEffects;

    let routeAction$: Observable<any>;

    let routerStub: jasmine.SpyObj<Router>;
    let locationStub: jasmine.SpyObj<Location>;

    beforeEach(waitForAsync(() => {
        routerStub = jasmine.createSpyObj<Router>('router', ['navigate']);
        locationStub = jasmine.createSpyObj<Location>('location', ['go', 'back', 'forward']);

        TestBed.configureTestingModule({
            providers: [
                {
                    provide: Router,
                    useValue: routerStub
                },
                {
                    provide: Location,
                    useValue: locationStub
                },
                provideMockActions(() => routeAction$),
                RouterEffects
            ]
        });

        routerStub.navigate.and.returnValue(Promise.resolve(true));

        effects = TestBed.inject(RouterEffects);
    }));

    it('should use Location.go()', marbles((m) => {
        routeAction$ = m.hot('-a', { a: new LocationGo({ path: '/test', query: 'search=random', state: {} }) });
        effects.locationGo$.subscribe(() => {
            expect(locationStub.go).toHaveBeenCalled();
        });
    }));

    it(`should verify will handle error and won't invoke Location.go()`, marbles((m) => {
        routeAction$ = m.hot('-#');

        effects.locationGo$.subscribe((v) => {
            expect(v).toBeTrue();
            expect(locationStub.go).not.toHaveBeenCalled();
        });
    }));

    it('should navigate back', marbles((m) => {
        routeAction$ = m.hot('-a', { a: new LocationBack() });
        effects.locationBack$.subscribe(() => {
            expect(locationStub.back).toHaveBeenCalled();
        });
    }));

    it(`should verify will handle error and won't invoke navigate back`, marbles((m) => {
        routeAction$ = m.hot('-#');

        effects.locationBack$.subscribe((v) => {
            expect(v).toBeTrue();
            expect(locationStub.back).not.toHaveBeenCalled();
        });
    }));

    it('should navigate forward', marbles((m) => {
        routeAction$ = m.hot('-a', { a: new LocationForward() });
        effects.locationForward$.subscribe(() => {
            expect(locationStub.forward).toHaveBeenCalled();
        });
    }));

    it(`should verify will handle error and won't invoke Location.forward()`, marbles((m) => {
        routeAction$ = m.hot('-#');

        effects.locationForward$.subscribe((v) => {
            expect(v).toBeTrue();
            expect(locationStub.forward).not.toHaveBeenCalled();
        });
    }));

    it('should navigate to path', marbles((m) => {
        const goAction = new RouterNavigate({
            commands: ['/domain', 'context', 'entity', 10, 'sub-entity', 7],
            extras: {
                queryParams: { value: 1 }
            }
        });

        routeAction$ = m.hot('a', { a: goAction });
        effects.routerNavigate$.subscribe(() => {
            expect(routerStub.navigate).toHaveBeenCalledWith([
                '/domain',
                'context',
                'entity',
                10,
                'sub-entity',
                7
            ], goAction.payload.extras);
        });
    }));

    it(`should verify will handle error and won't invoke router navigate`, marbles((m) => {
        routeAction$ = m.hot('-#');

        effects.routerNavigate$.subscribe((v) => {
            expect(v).toBeTrue();
            expect(routerStub.navigate).not.toHaveBeenCalled();
        });
    }));
});
