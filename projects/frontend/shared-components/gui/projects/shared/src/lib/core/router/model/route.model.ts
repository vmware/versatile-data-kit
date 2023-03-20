/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/member-ordering */

import { Params } from '@angular/router';

import { BaseRouterStoreState, RouterReducerState } from '@ngrx/router-store';

import { CollectionsUtil, PrimitivesNil } from '../../../utils';

import { Serializable, TaurusRouteData } from '../../../common';

/**
 * ** Route Segments Class.
 */
export class RouteSegments {
    public readonly routePath: string;
    public readonly data: TaurusRouteData;
    public readonly params: Params;
    public readonly queryParams: Params;
    public readonly parent?: RouteSegments;
    public readonly configPath?: string;

    /**
     * ** Constructor.
     */
    constructor(
        routePath: string,
        data: TaurusRouteData,
        params: Params,
        queryParams: Params,
        parent?: RouteSegments,
        configPath?: string
    ) {
        this.routePath = routePath ?? '';
        this.data = data || {};
        this.params = params || {};
        this.queryParams = queryParams || {};
        this.parent = parent;
        this.configPath = configPath;
    }

    /**
     * ** Factory method.
     */
    static of(
        routePath?: string,
        data?: TaurusRouteData,
        params?: Params,
        queryParams?: Params,
        parent?: RouteSegments,
        configPath?: string
    ): RouteSegments {
        return new RouteSegments(routePath, data, params, queryParams, parent, configPath);
    }

    /**
     * ** Factory method for empty RouteSegments.
     */
    static empty(): RouteSegments {
        return RouteSegments.of(null, null, null, null, null, null);
    }

    /**
     * ** Get RoutePath Segments.
     */
    get routePathSegments(): string[] {
        if (this.parent) {
            return ([] as string[]).concat(this.parent.routePathSegments, this.routePath).filter((path) => path);
        }

        return [this.routePath];
    }

    /**
     * ** Get ConfigPath Segments.
     */
    get configPathSegments(): string[] {
        if (this.parent) {
            return ([] as string[]).concat(this.parent.configPathSegments, this.configPath).filter((path) => path);
        }

        return [this.configPath];
    }

    /**
     * ** Get Data from Route configuration by key.
     *
     *      - Return first (closest) found key starting from the current one.
     */
    getData<T>(key: string): T {
        if (this.data[key]) {
            return this.data[key] as T;
        }

        if (this.parent) {
            return this.parent.getData<T>(key);
        }

        return undefined;
    }

    /**
     * ** Get url param by key.
     *
     *      - Return first (closest) found key starting from the current one.
     */
    getParam(key: string): string {
        if (this.params[key]) {
            return this.params[key] as string;
        }

        if (this.parent) {
            return this.parent.getParam(key);
        }

        return undefined;
    }

    /**
     * ** Get query param by key.
     */
    getQueryParam(key: string): string {
        if (this.queryParams[key]) {
            return this.queryParams[key] as string;
        }

        if (this.parent) {
            return this.parent.getQueryParam(key);
        }

        return undefined;
    }
}

/**
 * ** Route State Class.
 */
export class RouteState implements BaseRouterStoreState, Serializable<SerializedRouteState> {
    public readonly routeSegments: RouteSegments;
    public readonly url: string;

    /**
     * ** Constructor.
     */
    constructor(routeSegments: RouteSegments, url: string) {
        this.routeSegments = routeSegments ?? RouteSegments.empty();
        this.url = url ?? '';
    }

    /**
     * ** Factory method.
     */
    static of(routeSegments: RouteSegments, url: string): RouteState {
        return new RouteState(routeSegments, url);
    }

    /**
     * ** Factory method for empty State.
     */
    static empty(): RouteState {
        return RouteState.of(null, null);
    }

    /**
     * ** Get serialized queryString.
     */
    static serializeQueryParams(queryParams: unknown): string {
        const paramsKeys = Object.keys(queryParams);

        if (!paramsKeys.length) {
            return '';
        }

        return paramsKeys.map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(queryParams[key] as string)}`).join('&');
    }

    /**
     * ** Returns current RoutePath.
     */
    get routePath(): string {
        return this.routeSegments.routePath;
    }

    /**
     * ** Returns current Absolute RoutePath.
     */
    get absoluteRoutePath(): string {
        return RouteState._resolveAbsolutePath(this.routePathSegments);
    }

    /**
     * ** Returns the route paths for each route segment starting from the root.
     */
    get routePathSegments(): string[] {
        return this.routeSegments.routePathSegments;
    }

    /**
     * ** Returns current ConfigPath.
     */
    get configPath(): string {
        return this.routeSegments.configPath;
    }

    /**
     * ** Returns current Absolute ConfigPath.
     */
    get absoluteConfigPath(): string {
        return RouteState._resolveAbsolutePath(this.configPathSegments);
    }

    /**
     * ** Returns the config paths for each route segment starting from the root.
     */
    get configPathSegments(): string[] {
        return this.routeSegments.configPathSegments;
    }

    /**
     * ** Get all query params.
     */
    get queryParams(): Params {
        return this.routeSegments.queryParams;
    }

    /**
     * ** Get serialized queryString.
     */
    serializeQueryParams(): string {
        return RouteState.serializeQueryParams(this.queryParams);
    }

    /**
     * ** Get url including QueryParams.
     */
    getUrl(): string {
        return `${this.absoluteRoutePath}?${this.serializeQueryParams()}`;
    }

    /**
     * ** Get Data from Route configuration by key.
     *
     *      - Return first (closest) found key starting from first RouteSegment.
     */
    getData<T>(key: string): T {
        return this.routeSegments.getData<T>(key);
    }

    /**
     * ** Get url param by key.
     *
     *      - Return first (closest) found key starting from first RouteSegment.
     */
    getParam(key: string): string {
        return this.routeSegments.getParam(key);
    }

    /**
     * ** Get query param by key.
     */
    getQueryParam(key: string): string {
        return this.routeSegments.getQueryParam(key);
    }

    /**
     * ** Get Absolute ConfigPath.
     */
    getAbsoluteConfigPath(): string {
        return this.absoluteConfigPath;
    }

    /**
     * ** Get parent of current Absolute ConfigPath.
     */
    getParentAbsoluteConfigPath(): string {
        const configPathSegments = this.configPathSegments;
        configPathSegments.pop();

        return RouteState._resolveAbsolutePath(configPathSegments);
    }

    /**
     * ** Get Absolute RoutePath.
     */
    getAbsoluteRoutePath(): string {
        return RouteState._resolveAbsolutePath(this.routePathSegments);
    }

    /**
     * ** Get parent of current Absolute RoutePath.
     */
    getParentAbsoluteRoutePath(): string {
        const routePathSegments = this.routePathSegments;
        routePathSegments.pop();

        return RouteState._resolveAbsolutePath(routePathSegments);
    }

    /**
     * @inheritDoc
     */
    toJSON(): SerializedRouteState {
        return {
            url: this.url,
            routePath: this.routePath,
            absoluteRoutePath: this.absoluteRoutePath,
            routePathSegments: this.routePathSegments,
            configPath: this.configPath,
            absoluteConfigPath: this.absoluteConfigPath,
            configPathSegments: this.configPathSegments,
            queryParams: this.queryParams,
            routeSegments: this.routeSegments
        };
    }

    /**
     * ** Resolve Absolute RoutePath from given routePathSegments.
     */
    private static _resolveAbsolutePath(routePathSegments: string[]): string {
        const path = routePathSegments.join('/').replace(/^\/+/, '');

        if (path === '') {
            return '/';
        }

        return `/${path}`;
    }
}

/**
 * ** Router state.
 */
export class RouterState implements RouterReducerState<RouteState> {
    readonly state: RouteState;
    readonly navigationId: number;
    readonly previousStates: RouterState[];

    /**
     * ** Constructor.
     */
    constructor(state: RouteState, navigationId: number) {
        this.state = state ?? RouteState.empty();
        this.navigationId = navigationId ?? null;
        this.previousStates = [];
    }

    /**
     * ** Factory method.
     */
    static of(state: RouteState, navigationId: number): RouterState {
        return new RouterState(state, navigationId);
    }

    /**
     * ** Factory method for empty State.
     */
    static empty(): RouterState {
        return RouterState.of(null, null);
    }

    /**
     * ** Returns previous RouterState if exist otherwise null.
     *
     *      - Optional parameter could be provided to instruct which previous RouterState to return, default one is 0.
     *          - 0 means the first before current.
     *          - 1 means the second before current.
     *          - 2 means the third before current.
     *          - 3 ... etc...
     */
    getPrevious(index = 0): RouterState | null {
        const lookupIndex = CollectionsUtil.isNumber(index) ? index : 0;

        if (lookupIndex >= 0 && lookupIndex < this.previousStates.length) {
            return this.previousStates[lookupIndex];
        }

        return null;
    }

    /**
     * ** Append previous RouterState[] to current One.
     *
     *      - Internal API used in reducer, not for public use.
     */
    appendPrevious(routerState: RouterState): void {
        const previousStoredStates: RouterState[] = [...routerState.previousStates];
        const cleanedPreviousState = RouterState.of(routerState.state, routerState.navigationId);

        if (this.navigationId !== cleanedPreviousState.navigationId) {
            if (previousStoredStates.length >= 10) {
                previousStoredStates.pop();
            }

            previousStoredStates.unshift(cleanedPreviousState);
        }

        this.previousStates.length = 0;
        this.previousStates.push(...previousStoredStates);
    }
}

/**
 * ** Route state serialized.
 */
interface SerializedRouteState {
    url: string;
    routePath: string;
    absoluteRoutePath: string;
    routePathSegments: string[];
    configPath: string;
    absoluteConfigPath: string;
    configPathSegments: string[];
    queryParams: { [key: string]: PrimitivesNil };
    routeSegments: RouteSegments;
}
