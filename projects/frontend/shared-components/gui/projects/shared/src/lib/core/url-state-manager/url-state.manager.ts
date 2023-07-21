/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/naming-convention */

import { Location } from '@angular/common';

import { SE_LOCATION_CHANGE, SE_NAVIGATE, SystemEventDispatcher } from '../system-events';

export interface StateManagerParamValue {
    key: string;
    value: string;
    position: number;
}

/**
 * ** State Manager for Browser URL.
 *
 *   - Provides methods for easy appending/retrieving/removing of params and query params to the URL state.
 *   - Provides ability to serialize current state as URL href.
 */
export class URLStateManager {
    /**
     * ** Store value if URL Params State mutated since previous navigation.
     */
    public isParamsStateMutated = false;

    /**
     * ** Store value if URL QueryParams State mutated since previous navigation.
     */
    public isQueryParamsStateMutated = false;

    private readonly params: Map<string, StateManagerParamValue>;
    private readonly queryParams: Map<string, StateManagerParamValue>;
    private readonly locationHref: string;

    /**
     * ** Constructor.
     */
    constructor(public baseURL: string, public urlLocation: Location) {
        this.params = new Map<string, StateManagerParamValue>();
        this.queryParams = new Map<string, StateManagerParamValue>();

        this.locationHref = this.urlLocation.path();
    }

    /**
     * ** Returns current Browser URL href.
     */
    get URL(): string {
        if (this.baseURL) {
            return `${this.baseURL}${this.getParamsToString()}${this.getQueryParamsToString()}`;
        }

        return null;
    }

    /**
     * ** Replace current URL state to Browser URL.
     */
    replaceToUrl(): void {
        const browserCurrUrl = window.location.href;

        if (browserCurrUrl.endsWith(encodeURI(this.URL))) {
            return;
        }

        this.isParamsStateMutated = false;

        this.urlLocation.replaceState(this.URL);
    }

    /**
     * ** Apply current URL state to Browser URL.
     */
    locationToURL(): void {
        const browserCurrUrl = window.location.href;

        if (browserCurrUrl.endsWith(encodeURI(this.URL))) {
            return;
        }

        this.isParamsStateMutated = false;

        this._notifyForLocationChange();

        this.urlLocation.go(this.URL);
    }

    /**
     * ** Navigate through Angular Router with set URL state.
     */
    navigateToUrl(): Promise<boolean> {
        const browserCurrUrl = window.location.href;

        if (browserCurrUrl.endsWith(encodeURI(this.URL))) {
            return Promise.resolve(false);
        }

        this.isQueryParamsStateMutated = false;

        return SystemEventDispatcher.send(
            SE_NAVIGATE,
            {
                url: this.buildUrlWithParams(),
                extras: {
                    queryParams: this.getQueryParamsAsMap()
                }
            },
            1
        );
    }

    /**
     * ** Set query param to URL state.
     */
    setQueryParam(key: string, value: string, position = 1): void {
        this.isQueryParamsStateMutated = true;

        if (value) {
            this.queryParams.set(key, { key, value, position });
        } else {
            this.removeQueryParam(key);
        }
    }

    /**
     * ** Returns query param value for given key.
     */
    getQueryParam(key: string): string {
        if (this.queryParams.has(key)) {
            return this.queryParams.get(key).value;
        }

        return null;
    }

    /**
     * ** Removes query param from URL state.
     */
    removeQueryParam(key: string): void {
        if (this.queryParams.has(key)) {
            this.isQueryParamsStateMutated = true;

            this.queryParams.delete(key);
        }
    }

    /**
     * ** Clear stored queryParams.
     */
    clearQueryParams(): void {
        this.queryParams.clear();
    }

    /**
     * ** Set param to URL state.
     */
    setParam(key: string, value: string, position = 1): void {
        this.isParamsStateMutated = true;

        if (value) {
            this.params.set(key, { key, value, position });
        } else {
            this.removeParam(key);
        }
    }

    /**
     * ** Returns param value for given key.
     */
    getParam(key: string): string {
        if (this.params.has(key)) {
            return this.params.get(key).value;
        }

        return null;
    }

    /**
     * ** Removes query param from URL state.
     */
    removeParam(key: string): void {
        if (this.params.has(key)) {
            this.isParamsStateMutated = true;

            this.params.delete(key);
        }
    }

    /**
     * ** Clear stored params.
     */
    clearParams(): void {
        this.params.clear();
    }

    /**
     * ** Returns serialized params in string.
     */
    getParamsToString(): string {
        let paramString = '';

        this.getSortedByPosition(this.params).forEach((p) => {
            paramString += `/${p.value}`;
        });

        return paramString;
    }

    /**
     * ** Returns serialized queryParams in string.
     */
    getQueryParamsToString(): string {
        const sortedParams = this.getSortedByPosition(this.queryParams);

        let paramString = '';

        if (sortedParams.length > 0) {
            paramString = `?${sortedParams[0].key}=${sortedParams[0].value}`;

            for (let i = 1; i < sortedParams.length; i++) {
                const p = sortedParams[i];
                paramString += `&${p.key}=${p.value}`;
            }
        }

        return paramString;
    }

    /**
     * ** Returns query params in Map format.
     */
    getQueryParamsAsMap(): { [key: string]: string } {
        const sortedParams = this.getSortedByPosition(this.queryParams);
        const paramsMap = {};

        for (const paramsPair of sortedParams) {
            paramsMap[paramsPair.key] = paramsPair.value;
        }

        return paramsMap;
    }

    /**
     * ** Returns params in Map format.
     */
    getParamsAsMap(): { [key: string]: string } {
        const sortedParams = this.getSortedByPosition(this.params);
        const paramsMap = {};

        for (const paramsPair of sortedParams) {
            paramsMap[paramsPair.key] = paramsPair.value;
        }

        return paramsMap;
    }

    /**
     * ** Build url from base and provided params.
     */
    buildUrlWithParams(): string {
        if (this.baseURL) {
            return `${this.baseURL}${this.getParamsToString()}`;
        }

        return null;
    }

    /**
     * ** Change Base url.
     */
    changeBaseUrl(baseUrl: string): void {
        this.baseURL = baseUrl;
    }

    private getSortedByPosition(values: Map<string, StateManagerParamValue>): StateManagerParamValue[] {
        return Array.from(values.entries())
            .sort((p1, p2) => p1[1].position - p2[1].position)
            .map((e) => e[1]);
    }

    private _notifyForLocationChange(): void {
        const paramsMap = this.getParamsAsMap();
        const paramsSerialized = this.buildUrlWithParams();
        const queryParamsMap = this.getQueryParamsAsMap();
        const queryParamsSerialized = this.getQueryParamsToString();

        SystemEventDispatcher.post(SE_LOCATION_CHANGE, {
            url: this.URL,
            params: paramsMap ? paramsMap : {},
            paramsSerialized: paramsSerialized ? paramsSerialized : '',
            queryParams: queryParamsMap ? queryParamsMap : {},
            queryParamsSerialized: queryParamsSerialized ? queryParamsSerialized.replace(/^\?/, '') : ''
        });
    }
}
