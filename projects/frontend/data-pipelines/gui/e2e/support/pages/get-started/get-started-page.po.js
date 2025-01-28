/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { BasePagePO } from '../base/base-page.po';

export class GetStartedPagePO extends BasePagePO {
    /**
     * ** Returns instance of the page object.
     *
     * @returns {GetStartedPagePO}
     */
    static getPage() {
        return new GetStartedPagePO();
    }

    /**
     * ** Navigate to home page through URL and return instance of page object.
     *
     * @type {GetStartedPagePO}
     */
    static navigateTo() {
        cy.visit('/get-started');

        this.waitForApplicationBootstrap();
        this.waitForDataJobsApiGetReqInterceptor(3);

        this.waitForViewToRenderShort();

        return this.getPage();
    }

    /**
     * ** Navigate to home page through URL and return instance of page object.
     * ** Do not wait for bootstrap and interceptors
     * @type {GetStartedPagePO}
     */
    static navigateToNoBootstrap() {
        cy.visit('/get-started');
        this.waitForViewToRenderShort();
        return this.getPage();
    }
}
