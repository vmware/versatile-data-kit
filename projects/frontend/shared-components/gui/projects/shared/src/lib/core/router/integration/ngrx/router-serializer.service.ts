/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { RouterStateSnapshot } from '@angular/router';

import { RouterStateSerializer } from '@ngrx/router-store';

import { RouteState } from '../../model';
import { RouteStateFactory } from '../../factory';

/**
 * ** Shared Router Serializer implements NgRx RouterStateSerializer.
 */
@Injectable()
export class SharedRouterSerializer implements RouterStateSerializer<RouteState> {
    private readonly _routeStateFactory: RouteStateFactory;

    /**
     * ** Constructor.
     */
    constructor() {
        this._routeStateFactory = new RouteStateFactory();
    }

    /**
     * @inheritDoc
     */
    serialize(routerState: RouterStateSnapshot): RouteState {
        let routeSnapshot = routerState.root;

        while (routeSnapshot.firstChild) {
            routeSnapshot = routeSnapshot.firstChild;
        }

        return this._routeStateFactory.create(routeSnapshot, routerState.url);
    }
}
