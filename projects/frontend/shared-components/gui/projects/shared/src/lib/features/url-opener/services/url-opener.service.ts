/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { Params } from '@angular/router';

import { CookieService } from 'ngx-cookie-service';

import { CollectionsUtil } from '../../../utils';

import { TaurusObject } from '../../../common';

import { NavigationService } from '../../../core';

import { ConfirmationOutputModel, ConfirmationService } from '../../confirmation';

import { UrlOpenerModel, UrlOpenerTarget } from '../model';

/**
 * ** Internal service model.
 */
interface NextStepModel {
    /**
     * ** Is provided url external.
     */
    external: boolean;
    /**
     * ** Sanitized url.
     *
     *      - Could be use in future if some sanitization is needed for some special cases.
     */
    sanitizedUrl: string;
    /**
     * ** Does url be open in new tab.
     */
    newTab: boolean;
}

/**
 * ** Url Opener Service that opens internal and external urls depends on provided instructions.
 *
 *      - Utilizes <code>Promise<boolean></code> for communication to invoker that is resolved after navigation.
 *      - Internal urls could be open directly without confirmation or explicitly with confirmation,
 *              while external are always prompt for confirmation it there is no option to skip confirmation for next navigations,
 *              and User prompt such confirmation to be skipped.
 *      - Skipped confirmation are persisted in Cookie storage as Origin for external urls and as Url for internal urls.
 *      - Returned Promise is resolved upon navigation ends with true (successful navigation) or false (unsuccessful navigation),
 *              or rejected with value string if it's on User behalf,
 *              or if there is some internal handled error it will be rejected with instance of Error and message of the specific problem.
 */
@Injectable()
export class UrlOpenerService extends TaurusObject {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'UrlOpenerService';

    /**
     * ** Application origin, resolved upon service declaration.
     *
     * @private
     */
    private readonly _origin: string;

    /**
     * ** Cookie key where service state is persisted, resolved upon service declaration.
     *
     *      - It's service Class Name encoded to Base64.
     *
     * @private
     */
    private readonly _cookieKey: string;

    /**
     * ** Application state, for which origins/urls confirmation should be skipped.
     *
     * @private
     */
    private _skippedOriginsUrlsMap: Record<string, '1'> = {};

    /**
     * ** Constructor.
     */
    constructor(
        private readonly navigationService: NavigationService,
        private readonly confirmationService: ConfirmationService,
        private readonly cookieService: CookieService
    ) {
        super(UrlOpenerService.CLASS_NAME);

        try {
            this._origin = window.location.origin;
            this._cookieKey = UrlOpenerService._encodeBase64(UrlOpenerService.CLASS_NAME);
        } catch (e) {
            console.error(`${UrlOpenerService.CLASS_NAME}: Potential bug found, cannot identify Cookie key and Origin`);
        }
    }

    /**
     * ** Open provided Url to default _blank target.
     *
     *      - Internal urls are open directly without confirmation, while external are always prompt for confirmation.
     *      - Returned Promise is resolved upon navigation ends with true (successful navigation) or false (unsuccessful navigation),
     *              or if there is some internal handled error it will be rejected with instance of Error and message of the specific problem.
     *      - Every url which starts with pattern http:// or https:// and its origin is different from Application origin is marked as external url.
     *      - Everything else is internal url.
     */
    open(url: string): Promise<boolean>;
    /**
     * ** Open provided Url using provided target _self or _blank
     *
     *      - Internal urls are open directly without confirmation, while external are always prompt for confirmation.
     *      - Returned Promise is resolved upon navigation ends with true (successful navigation) or false (unsuccessful navigation),
     *              or if there is some internal handled error it will be rejected with instance of Error and message of the specific problem.
     *      - Every url which starts with pattern http:// or https:// and its origin is different from Application origin is marked as external url.
     *      - Everything else is internal url.
     */
    open(url: string, target: UrlOpenerTarget): Promise<boolean>;
    /**
     * ** Open provided Url using provided target _self or _blank and utilizing provided model and service will set some defaults for optional fields.
     *
     *      - Internal urls could be open directly without confirmation or explicitly with confirmation depend on provided model,
     *              while external are always prompt for confirmation it there is no option to skip confirmation for next navigations,
     *              and User prompt such confirmation to be skipped.
     *      - Skipped confirmation are persisted in Cookie storage as Origin for external urls and as Url for internal urls.
     *      - Returned Promise is resolved upon navigation ends with true (successful navigation) or false (unsuccessful navigation),
     *              or rejected with value string if it's on User behalf when confirmation is closable or with button cancel,
     *              or if there is some internal handled error it will be rejected with instance of Error and message of the specific problem.
     */
    open(url: string, target: UrlOpenerTarget, model: UrlOpenerModel): Promise<boolean>;
    /**
     * @inheritDoc
     */
    open(url: string, target: UrlOpenerTarget = '_blank', model: UrlOpenerModel = null): Promise<boolean> {
        const _model: UrlOpenerModel = { ...(model ?? {}) } as UrlOpenerModel;
        const _nextStep = this._resolveNextStep(url, target);

        if (_nextStep.external) {
            return this._executeExternalNavigation(url, _model, _nextStep);
        }

        return this._executeInternalNavigation(url, _model, _nextStep);
    }

    /**
     * ** Initialize service.
     *
     *      - Should be invoked only once.
     *      - Ideal place for invoking is <code>AppComponent.ngOnInit()</code>.
     */
    initialize(): void {
        const extractSkippedOriginsMap = this._extractSkippedUrlsMap();
        if (extractSkippedOriginsMap) {
            this._skippedOriginsUrlsMap = extractSkippedOriginsMap;
        }
    }

    private _resolveNextStep(url: string, target: UrlOpenerTarget): NextStepModel {
        let newTab = false;
        let external = false;

        if (target === '_blank') {
            newTab = true;
        }

        if (new RegExp(`^${this._origin}`).test(url)) {
            external = false;
        } else if (/^(http|https):\/?\/?/.test(url)) {
            external = true;
        }

        return {
            newTab,
            external,
            sanitizedUrl: url
        };
    }

    private _executeExternalNavigation(url: string, model: UrlOpenerModel, nextStep: NextStepModel): Promise<boolean> {
        const urlOriginData = this._getExternalUrlOriginData(url);

        let confirmationPromise: Promise<ConfirmationOutputModel>;

        if (urlOriginData === '1') {
            confirmationPromise = Promise.resolve({ doNotShowFutureConfirmation: false });
        } else {
            if (!CollectionsUtil.isStringWithContent(model.title)) {
                model.title = `Proceed to <code>${url}</code>`;
            }

            if (CollectionsUtil.isNil(model.closable)) {
                model.closable = true;
            }

            if (CollectionsUtil.isNil(model.confirmBtnModel)) {
                model.confirmBtnModel = {
                    text: 'Proceed'
                };
            } else if (!CollectionsUtil.isStringWithContent(model.confirmBtnModel.text)) {
                model.confirmBtnModel.text = 'Proceed';
            }

            confirmationPromise = this.confirmationService.confirm(model);
        }

        return confirmationPromise.then((data) => {
            if (data.doNotShowFutureConfirmation) {
                this._persistSkippedExternalUrlOrigin(url);
            }

            const isSuccessful = UrlOpenerService._openExternalUrl(nextStep.sanitizedUrl, nextStep.newTab);
            if (isSuccessful) {
                return true;
            }

            return Promise.reject(new Error(`${UrlOpenerService.CLASS_NAME}: Exception thrown cannot open external url`));
        });
    }

    private _executeInternalNavigation(url: string, model: UrlOpenerModel, nextStep: NextStepModel): Promise<boolean> {
        const urlData = this._getInternalUrlData(url);

        let confirmationPromise: Promise<ConfirmationOutputModel>;

        if (urlData === '1' || !model.explicitConfirmation) {
            confirmationPromise = Promise.resolve({ doNotShowFutureConfirmation: false });
        } else {
            if (!CollectionsUtil.isStringWithContent(model.title)) {
                model.title = `Proceed to <code>${url}</code>`;
            }

            if (CollectionsUtil.isNil(model.confirmBtnModel)) {
                model.confirmBtnModel = {
                    text: 'Proceed'
                };
            } else if (!CollectionsUtil.isStringWithContent(model.confirmBtnModel.text)) {
                model.confirmBtnModel.text = 'Proceed';
            }

            confirmationPromise = this.confirmationService.confirm(model);
        }

        return confirmationPromise.then((data) => {
            if (data.doNotShowFutureConfirmation) {
                this._persistSkippedInternalUrl(url);
            }

            if (nextStep.newTab) {
                const isSuccessful = UrlOpenerService._openExternalUrl(nextStep.sanitizedUrl, true);
                if (isSuccessful) {
                    return true;
                }

                return Promise.reject(
                    new Error(`${UrlOpenerService.CLASS_NAME}: Exception thrown, cannot open Super Collider url in a new tab`)
                );
            }

            const _queryParams: Params = {};
            let _sanitizedUrl: string = nextStep.sanitizedUrl;

            try {
                const queryStringStartIndex = url.indexOf('?');

                if (queryStringStartIndex !== -1) {
                    _sanitizedUrl = url.substring(0, queryStringStartIndex);
                    const queryString = url.substring(queryStringStartIndex);
                    new URLSearchParams(queryString).forEach((value, key) => {
                        _queryParams[key] = value;
                    });
                }
            } catch (e) {
                console.error(
                    `${UrlOpenerService.CLASS_NAME}: Potential bug found, Exception thrown while extracting query string for internal navigation`
                );
            }

            return this.navigationService.navigate(_sanitizedUrl, { queryParams: _queryParams });
        });
    }

    private _getExternalUrlOriginData(url: string): '1' | null {
        const urlOrigin = UrlOpenerService._getUrlOrigin(url);

        if (!this._skippedOriginsUrlsMap[urlOrigin]) {
            return null;
        }

        return this._skippedOriginsUrlsMap[urlOrigin];
    }

    private _persistSkippedExternalUrlOrigin(url: string): void {
        const urlOrigin = UrlOpenerService._getUrlOrigin(url);

        if (!urlOrigin) {
            return;
        }

        this._persistSkippedInternalUrl(urlOrigin);
    }

    private _getInternalUrlData(url: string): '1' | null {
        if (!this._skippedOriginsUrlsMap[url]) {
            return null;
        }

        return this._skippedOriginsUrlsMap[url];
    }

    private _persistSkippedInternalUrl(url: string): void {
        if (this._skippedOriginsUrlsMap[url]) {
            return;
        }

        this._skippedOriginsUrlsMap[url] = '1';

        this._persistSkippedUrlsMap();
    }

    private _extractSkippedUrlsMap(): Record<string, '1'> {
        const extractedOriginsMap = this.cookieService.get(this._cookieKey);
        if (!extractedOriginsMap) {
            return null;
        }

        const decodedOriginsMap = UrlOpenerService._decodeBase64(extractedOriginsMap);
        if (!decodedOriginsMap) {
            return null;
        }

        const parsedOriginsMap = UrlOpenerService._parseToJSON<Record<string, '1'>>(decodedOriginsMap);
        if (!parsedOriginsMap) {
            return null;
        }

        return parsedOriginsMap;
    }

    private _persistSkippedUrlsMap(): void {
        if (!this._skippedOriginsUrlsMap) {
            return;
        }

        const serializedOriginsMap = UrlOpenerService._serializeObject(this._skippedOriginsUrlsMap);
        if (!serializedOriginsMap) {
            return;
        }

        const encodedOriginsMap = UrlOpenerService._encodeBase64(serializedOriginsMap);
        if (!encodedOriginsMap) {
            return;
        }

        this.cookieService.set(this._cookieKey, encodedOriginsMap);
    }

    private static _openExternalUrl(url: string, newTab: boolean): boolean {
        try {
            window.open(url, newTab ? '_blank' : '_self', 'noopener');

            return true;
        } catch (e) {
            console.error(
                `${UrlOpenerService.CLASS_NAME}: Cannot open external url, check your Browser security config if allows opening new tabs`
            );

            return false;
        }
    }

    private static _getUrlOrigin(url: string): string {
        try {
            const _url = new URL(url);

            return _url.origin;
        } catch (e) {
            console.error(`${UrlOpenerService.CLASS_NAME}: Potential bug found, cannot extract origin from url`);

            return null;
        }
    }

    private static _encodeBase64(value: string): string {
        if (!value) {
            return null;
        }

        try {
            return btoa(value);
        } catch (e) {
            console.error(`${UrlOpenerService.CLASS_NAME}: Potential bug found, provided value cannot be encoded to base64`);

            return null;
        }
    }

    private static _decodeBase64(value: string): string {
        if (!value) {
            return null;
        }

        try {
            return atob(value);
        } catch (e) {
            console.error(`${UrlOpenerService.CLASS_NAME}: Potential bug found, provided value cannot be decoded from base64`);

            return null;
        }
    }

    private static _serializeObject(value: unknown): string {
        if (!value) {
            return null;
        }

        try {
            return JSON.stringify(value);
        } catch (e) {
            console.error(`${UrlOpenerService.CLASS_NAME}: Potential bug found, cannot serialize provided object`);

            return null;
        }
    }

    private static _parseToJSON<T>(value: string): T {
        if (!value) {
            return null;
        }

        try {
            return JSON.parse(value) as T;
        } catch (e) {
            console.error(`${UrlOpenerService.CLASS_NAME}: Potential bug found, cannot parse provided JSON`);

            return null;
        }
    }
}
