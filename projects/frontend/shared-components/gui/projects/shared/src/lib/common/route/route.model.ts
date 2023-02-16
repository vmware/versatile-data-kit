

/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/no-explicit-any */

import { Data, NavigationExtras, Params, Route } from '@angular/router';

import { Replacer } from '../interfaces';

/**
 * ** Interface for Navigate back command.
 */
export interface TaurusNavigateAction<T extends string = string> {
    /**
     * ** Path / Path commands where user should be navigated, returned or redirected.
     *
     *      - If path is '$.current' - current loaded path will be use.
     *      - If path is '$.requested' - requested path will be use.
     *      - If path is '$.parent' - parent of the current path will be use.
     *      - Any other string - use at is and assume it as path for navigation (URL path)
     *          <Additional handling could be done from subclasses implementation, and also functionality could be extended.>
     */
    path: string | '$.current' | '$.requested' | '$.parent';

    /**
     * ** Replacers to tune and finalize navigate back Path / Path commands.
     */
    replacers?: Array<Replacer<T>>;

    /**
     * ** Optional query params for navigation action.
     */
    queryParams?: Params;

    /**
     * ** Optional instruction for queryParams handling.
     *
     *      - If not provided will fallback to default one 'merge'.
     *      - If provided and its value is null, it won't do any handling for queryParams.
     */
    queryParamsHandling?: NavigationExtras['queryParamsHandling'];

    /**
     * ** Optional instruction whether to use resolved path or config path.
     *
     *      - TRUE - will use config path, which means use it as it's configured in the routing modules.
     *      - FALSE - will use resolved path to the current point.
     */
    useConfigPath?: boolean;
}

/**
 * ** Taurus Route data with navigate to command.
 */
export interface TaurusRouteNavigateToData {
    /**
     * ** Field that has Navigate to command.
     */
    navigateTo?: TaurusNavigateAction;
}

/**
 * ** Taurus Route data with navigate back command.
 */
export interface TaurusRouteNavigateBackData {
    /**
     * ** Field that has Navigate back command.
     */
    navigateBack?: TaurusNavigateAction;
}

/**
 * ** Taurus Route data with redirect command.
 */
export interface TaurusRouteRedirectData {
    /**
     * ** Field that has Redirect command.
     */
    redirect?: TaurusNavigateAction;
}

/**
 * ** Custom type for Route Data with Generics.
 */
export type TaurusRouteData<T extends Record<string, any> = Record<string, any>> =
    T
    & TaurusRouteNavigateToData
    & TaurusRouteNavigateBackData
    & TaurusRouteRedirectData
    & Data;

/**
 * ** Taurus Route config.
 */
export interface TaurusRoute<T extends TaurusRouteData = TaurusRouteData> extends Route {
    /**
     * @inheritDoc
     *
     * ** Static data configured per Route.
     */
    data?: T;

    /**
     * @inheritDoc
     *
     * ** Children Route configs object.
     */
    children?: TaurusRoutes<T>;
}

/**
 * ** Taurus Routes configs.
 */
export type TaurusRoutes<T extends TaurusRouteData = TaurusRouteData> = TaurusRoute<T>[];
