

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable arrow-body-style,
                  prefer-arrow/prefer-arrow-functions,
                  @angular-eslint/component-class-suffix,
                  @typescript-eslint/no-explicit-any */

import { Type } from '@angular/core';

import { ActivatedRouteSnapshot, Data, Params, Route, UrlSegment } from '@angular/router';

import { CollectionsUtil } from '../../utils';

type ComponentType = Type<any> | string | null;

export const createRouteSnapshot = ({
                                        url = [new UrlSegment('entity/23', {})] as UrlSegment[],
                                        data = { paramKey: 'prime' } as Data,
                                        params = { entityId: 23 } as Params,
                                        queryParams = { search: 'test-team' } as Params,
                                        outlet = 'router-outlet' as string,
                                        component = ComponentStub as ComponentType,
                                        routeConfig = new RouteConfigStub('entity/23', ComponentStub, 'router-outlet'),
                                        firstChild = null as ActivatedRouteSnapshot,
                                        parent = undefined as ActivatedRouteSnapshot
                                    }): ActivatedRouteSnapshot => {

    // @ts-ignore
    return new ActivatedRouteSnapshotStub({
        url,
        data,
        params,
        queryParams,
        outlet,
        component,
        routeConfig,
        firstChild,
        parent: CollectionsUtil.isUndefined(parent)
            ? createRouteSnapshot({
                url: [new UrlSegment('domain/context', {})],
                data: {},
                params: {},
                queryParams: {},
                outlet: 'router-outlet',
                component: null,
                routeConfig: new RouteConfigStub('domain/context', null, 'router-outlet'),
                firstChild: null,
                parent: null
            })
            : null
    });
};

export class ComponentStub {
}

interface RouteSnapshotStub {
    url: UrlSegment[];
    data: Data;
    params: Params;
    queryParams: Params;
    outlet: string;
    component: Type<any> | string | null;
    routeConfig: Route | null;
    firstChild: ActivatedRouteSnapshot;
    parent: ActivatedRouteSnapshot;
}

export class ActivatedRouteSnapshotStub extends ActivatedRouteSnapshot {
    override url: UrlSegment[];
    override data: Data;
    override params: Params;
    override queryParams: Params;
    override outlet: string;
    // @ts-ignore
    override component: Type<any> | string | null;
    override readonly routeConfig: Route | null;

    override get parent(): ActivatedRouteSnapshot | null {
        return this._parent;
    }

    override set parent(parent: ActivatedRouteSnapshot) {
        this._parent = parent;
    }

    override get firstChild(): ActivatedRouteSnapshot | null {
        return this._firstChild;
    }

    protected _parent: ActivatedRouteSnapshot;
    protected _firstChild: ActivatedRouteSnapshot;

    constructor(snapshot: RouteSnapshotStub) {
        super();

        this.url = snapshot.url;
        this.data = snapshot.data;
        this.params = snapshot.params;
        this.queryParams = snapshot.queryParams;
        this.outlet = snapshot.outlet;
        this.component = snapshot.component;
        this.routeConfig = snapshot.routeConfig;
        this._firstChild = snapshot.firstChild;
        this._parent = snapshot.parent;

        if (snapshot.firstChild instanceof ActivatedRouteSnapshotStub) {
            // @ts-ignore
            snapshot.firstChild.parent = this;
        }
    }

    override toString(): string {
        return super.toString();
    }
}

export class RouteConfigStub implements Route {
    path: string;
    component: Type<any>;
    outlet: string;

    constructor(path: string,
                component: Type<any>,
                outlet: string) {
        this.path = path;
        this.component = component;
        this.outlet = outlet;
    }
}
