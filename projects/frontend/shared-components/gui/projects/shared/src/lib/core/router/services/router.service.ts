/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Directive, Injectable } from '@angular/core';

import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { Store } from '@ngrx/store';

import { TaurusObject } from '../../../common';

import { STORE_ROUTER, StoreState } from '../../ngrx';

import { RouterState, RouteState } from '../model';

/**
 * ** Router Service.
 */
@Directive()
// eslint-disable-next-line @angular-eslint/directive-class-suffix
export abstract class RouterService extends TaurusObject {
    protected static _routerState: RouterState = RouterState.empty();

    /**
     * ** Will return current Router.
     */
    static get(): RouterState {
        return RouterService._routerState;
    }

    /**
     * ** Will return current Route State.
     */
    static getState(): RouteState {
        return RouterService._routerState.state;
    }

    /**
     * ** Will return Observable with NgRx Route State.
     */
    abstract get(): Observable<RouterState>;

    /**
     * ** Will return Observable with Route State.
     */
    abstract getState(): Observable<RouteState>;

    /**
     * ** Will initialize service.
     */
    abstract initialize(): void;
}

/**
 * @inheritDoc
 */
@Injectable()
export class RouterServiceImpl extends RouterService {
    constructor(private readonly store$: Store<StoreState>) {
        super();
    }

    /**
     * @inheritDoc
     */
    get(): Observable<RouterState> {
        return this.store$.select(STORE_ROUTER);
    }

    /**
     * @inheritDoc
     */
    getState(): Observable<RouteState> {
        return this.get().pipe(map((data) => data.state));
    }

    /**
     * @inheritDoc
     */
    initialize(): void {
        this.cleanSubscriptions();

        this.subscriptions.push(
            this.get().subscribe((state) => {
                RouterService._routerState = state;
            })
        );
    }
}
