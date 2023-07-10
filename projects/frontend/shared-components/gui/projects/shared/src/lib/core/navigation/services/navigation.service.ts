/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { ActivatedRoute, ActivatedRouteSnapshot, NavigationExtras, Router } from '@angular/router';

import { take } from 'rxjs/operators';

import { ArrayElement, CollectionsUtil } from '../../../utils';

import { Replacer, TaurusNavigateAction } from '../../../common';

import { SE_NAVIGATE, SystemEventHandler, SystemEventHandlerClass, SystemEventNavigatePayload } from '../../system-events';

import { RouterService, RouteState } from '../../router';
import { RouteStateFactory } from '../../router/factory';

/**
 * ** Service should be provided from the Root injector in Application.
 */
@Injectable()
@SystemEventHandlerClass()
export class NavigationService {
    private readonly _routeStateFactory: RouteStateFactory;

    /**
     * ** Constructor.
     */
    constructor(private readonly router: Router, private readonly routerService: RouterService) {
        this._routeStateFactory = new RouteStateFactory();
    }

    /**
     * ** Intercept SE_NAVIGATE Event and handle (react) on it.
     */
    @SystemEventHandler(SE_NAVIGATE)
    _navigationSystemEventHandler_(payload: SystemEventNavigatePayload): Promise<boolean> {
        if (CollectionsUtil.isNil(payload)) {
            return Promise.resolve(false);
        }

        return this.navigate(payload.url, payload.extras);
    }

    /**
     * ** Navigate to url with provided extras.
     */
    navigate(url: string | string[], extras?: NavigationExtras): Promise<boolean> {
        let urlChunks: string[];

        if (CollectionsUtil.isArray(url)) {
            urlChunks = url.map((v, i) => (i === 0 ? `/${v.replace(/^\//, '')}` : v));
        } else if (CollectionsUtil.isString(url)) {
            if (url.trim() === '/') {
                urlChunks = ['/'];
            } else {
                urlChunks = url
                    .split('/')
                    .filter((v) => !!v)
                    .map((v, i) => (i === 0 ? `/${v}` : v));
            }
        } else {
            return Promise.resolve(false);
        }

        return CollectionsUtil.isLiteralObject(extras) ? this.router.navigate(urlChunks, extras) : this.router.navigate(urlChunks);
    }

    /**
     * ** Navigate to using Route config, RouteState and leveraging provided optional replaceValueResolver.
     *
     * @param replaceValues is Object with mapping between Replacer.replaceValue key pointer to dynamic value specific for the Page.
     *      - What does it mean?
     *          Replacer has searchValue and replaceValue. When searchValue match, it replace with replaceValue, but
     *              replaceValue could be something like '$.team', '$.job', '{0}', '{1}' etc... dynamic params, so those params
     *              could be key in this Map to construct correct url depending of the logic in RouteConfig.
     * <p>
     * Important!!!
     *      - If replaceValues is not provided or some key doesn't exist there, replaceValue would be use as it is in the RouteConfig.
     * </p>
     * <p></p>
     * @param activatedRoute is optional and could be provided if you want those state to be used to extract RouteConfig and NavigationAction.
     */
    navigateTo(
        replaceValues?: { [key: string]: ArrayElement<TaurusNavigateAction['replacers']>['replaceValue'] },
        activatedRoute?: ActivatedRoute | ActivatedRouteSnapshot
    ): Promise<boolean> {
        return this._navigateWithAction(replaceValues, activatedRoute, 'navigateTo');
    }

    /**
     * ** Navigate back using Route config, RouteState and leveraging provided optional replaceValueResolver.
     *
     * @param replaceValues is Object with mapping between Replacer.replaceValue key pointer to dynamic value specific for the Page.
     *      - What does it mean?
     *          Replacer has searchValue and replaceValue. When searchValue match, it replace with replaceValue, but
     *              replaceValue could be something like '$.team', '$.job', '{0}', '{1}' etc... dynamic params, so those params
     *              could be key in this Map to construct correct url depending of the logic in RouteConfig.
     * <p>
     * Important!!!
     *      - If replaceValues is not provided or some key doesn't exist there, replaceValue would be use as it is in the RouteConfig.
     * </p>
     * <p></p>
     * @param activatedRoute is optional and could be provided if you want those state to be used to extract RouteConfig and NavigationAction.
     */
    navigateBack(
        replaceValues?: { [key: string]: ArrayElement<TaurusNavigateAction['replacers']>['replaceValue'] },
        activatedRoute?: ActivatedRoute | ActivatedRouteSnapshot
    ): Promise<boolean> {
        return this._navigateWithAction(replaceValues, activatedRoute, 'navigateBack');
    }

    /**
     * ** Redirect using Route config, RouteState and leveraging provided optional replaceValueResolver.
     *
     * @param replaceValues is Object with mapping between Replacer.replaceValue key pointer to dynamic value specific for the Page.
     *      - What does it mean?
     *          Replacer has searchValue and replaceValue. When searchValue match, it replace with replaceValue, but
     *              replaceValue could be something like '$.team', '$.job', '{0}', '{1}' etc... dynamic params, so those params
     *              could be key in this Map to construct correct url depending of the logic in RouteConfig.
     * <p>
     * Important!!!
     *      - If replaceValues is not provided or some key doesn't exist there, replaceValue would be use as it is in the RouteConfig.
     * </p>
     * <p></p>
     * @param activatedRoute is optional and could be provided if you want those state to be used to extract RouteConfig and NavigationAction.
     */
    redirect(
        replaceValues?: { [key: string]: ArrayElement<TaurusNavigateAction['replacers']>['replaceValue'] },
        activatedRoute?: ActivatedRoute | ActivatedRouteSnapshot
    ): Promise<boolean> {
        return this._navigateWithAction(replaceValues, activatedRoute, 'redirect');
    }

    /**
     * ** Resolve NavigationAction using Route config, RouteState and leveraging provided optional replaceValueResolver.
     * @param navigateActionType is the type of the NavigationAction we want to resolve from Route config.
     * @param replaceValues is Object with mapping between Replacer.replaceValue key pointer to dynamic value specific for the Page.
     *      - What does it mean?
     *          Replacer has searchValue and replaceValue. When searchValue match, it replace with replaceValue, but
     *              replaceValue could be something like '$.team', '$.job', '{0}', '{1}' etc... dynamic params, so those params
     *              could be key in this Map to construct correct url depending of the logic in RouteConfig.
     * <p>
     * Important!!!
     *      - If replaceValues is not provided or some key doesn't exist there, replaceValue would be use as it is in the RouteConfig.
     * </p>
     * <p></p>
     * @param activatedRoute is optional and could be provided if you want those state to be used to extract RouteConfig and NavigationAction.
     */
    resolveNavigateActionUrl(
        navigateActionType: 'navigateTo' | 'navigateBack' | 'redirect',
        replaceValues?: { [key: string]: ArrayElement<TaurusNavigateAction['replacers']>['replaceValue'] },
        activatedRoute?: ActivatedRoute | ActivatedRouteSnapshot | RouteState
    ): Promise<[string, NavigationExtras]> {
        const _replaceValues = CollectionsUtil.isLiteralObject(replaceValues) ? replaceValues : {};

        return this._extractRouteState(activatedRoute)
            .then((state) => this._constructNavigateParameters(state, navigateActionType))
            .then((params) => this._resolveNavigateValues(params.url, params.replacers, _replaceValues, params.navigationExtras));
    }

    /**
     * ** Initialize the Service without any operation, just to create singleton Service instance.
     *
     *   - It should be done in the root of the project only once.
     *   - Possible place is AppComponent or some root initializer guard.
     */
    initialize(): void {
        this.routerService.initialize();
    }

    private _navigateWithAction(
        replaceValues: { [key: string]: ArrayElement<TaurusNavigateAction['replacers']>['replaceValue'] },
        activatedRoute: ActivatedRoute | ActivatedRouteSnapshot,
        dataKey: 'navigateTo' | 'navigateBack' | 'redirect'
    ): Promise<boolean> {
        return this.resolveNavigateActionUrl(dataKey, replaceValues, activatedRoute)
            .then()
            .then(([url, navigationExtras]) => this.navigate(url, navigationExtras))
            .catch((error) => {
                console.error(error);

                return false;
            });
    }

    private _extractRouteState(activatedRoute: ActivatedRoute | ActivatedRouteSnapshot | RouteState): Promise<RouteState> {
        // NOTICE
        // this piece of code is needed for Guards cases usage.
        // Use params and data from Guard RouteState instead from RouterService because
        // RouterService state is populated after all guards are resolved
        if (CollectionsUtil.isDefined(activatedRoute)) {
            if (activatedRoute instanceof RouteState) {
                return Promise.resolve(activatedRoute);
            }

            return Promise.resolve(
                this._routeStateFactory.create(activatedRoute instanceof ActivatedRoute ? activatedRoute.snapshot : activatedRoute, null)
            );
        }

        return this.routerService
            .getState()
            .pipe(take(1))
            .toPromise()
            .then((state) => state);
    }

    // eslint-disable-next-line max-len
    private _constructNavigateParameters(
        state: RouteState,
        dataKey: 'navigateTo' | 'navigateBack' | 'redirect'
    ): Promise<NavigationParameters> {
        const navigateAction = state.getData<TaurusNavigateAction>(dataKey);
        const navigationExtras: NavigationExtras = { queryParamsHandling: 'merge' };

        let url: string;
        let replacers: Array<Replacer<string>> = [];

        if (CollectionsUtil.isDefined(navigateAction)) {
            url = this._resolveNavigateUrl(state, dataKey, navigateAction);

            if (CollectionsUtil.isArray(navigateAction.replacers)) {
                replacers = navigateAction.replacers;
            }

            this._appendNavigateExtras(state, navigationExtras, navigateAction);
        } else if (dataKey === 'navigateBack') {
            url = state.getParentAbsoluteRoutePath();
        } else {
            return Promise.reject('Cannot navigate without NavigationAction');
        }

        return Promise.resolve({
            url,
            replacers,
            navigationExtras
        });
    }

    private _resolveNavigateUrl(
        state: RouteState,
        dataKey: 'navigateTo' | 'navigateBack' | 'redirect',
        navigateAction: TaurusNavigateAction
    ): string {
        if (dataKey === 'redirect' || dataKey === 'navigateBack') {
            if (navigateAction.path === '$.parent' || navigateAction.path === '$.requested') {
                return navigateAction.useConfigPath ? state.getParentAbsoluteConfigPath() : state.getParentAbsoluteRoutePath();
            }

            if (navigateAction.path === '$.current') {
                return navigateAction.useConfigPath ? state.getAbsoluteConfigPath() : state.getAbsoluteRoutePath();
            }

            return navigateAction.path;
        }

        if (navigateAction.path === '$.current') {
            return navigateAction.useConfigPath ? state.getAbsoluteConfigPath() : state.getAbsoluteRoutePath();
        }

        return navigateAction.path;
    }

    // eslint-disable-next-line max-len
    private _appendNavigateExtras(state: RouteState, navigationExtras: NavigationExtras, navigateAction: TaurusNavigateAction): void {
        if (CollectionsUtil.isString(navigateAction.queryParamsHandling)) {
            navigationExtras.queryParamsHandling = navigateAction.queryParamsHandling;

            if (navigationExtras.queryParamsHandling === 'merge') {
                navigationExtras.queryParams = {
                    ...state.queryParams,
                    ...(navigateAction.queryParams ?? {})
                };
            } else if (navigationExtras.queryParamsHandling !== 'preserve') {
                navigationExtras.queryParams = navigateAction.queryParams ?? {};
            }
        } else if (CollectionsUtil.isNull(navigateAction.queryParamsHandling)) {
            delete navigationExtras.queryParamsHandling;
        } else {
            navigationExtras.queryParams = {
                ...state.queryParams,
                ...(navigateAction.queryParams ?? {})
            };
        }
    }

    private _resolveNavigateValues(
        path: string,
        replacers: Array<Replacer<string>>,
        replaceValues: { [key: string]: ArrayElement<TaurusNavigateAction['replacers']>['replaceValue'] },
        navigationExtras: NavigationExtras
    ): Promise<[string, NavigationExtras]> {
        let resolvedPath: string;

        if (CollectionsUtil.isString(path)) {
            resolvedPath = path;
        } else {
            resolvedPath = '/';

            console.error(`RouteConfig error! NavigationAction config, "path" property is missing.`);
        }

        for (const replacer of replacers) {
            const replaceValue = replaceValues[replacer.replaceValue] ?? replacer.replaceValue;

            resolvedPath = resolvedPath.replace(replacer.searchValue, replaceValue);
        }

        return Promise.resolve([resolvedPath, navigationExtras]);
    }
}

interface NavigationParameters {
    url: string;
    replacers: Array<Replacer<string>>;
    navigationExtras: NavigationExtras;
}
