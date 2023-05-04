/*
 * Copyright 2021-2023 VMware, Inc.
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

    static navigateToNoWaitDataJobs() {
        cy.visit('/get-started');

        this.waitForApplicationBootstrap();
        // this.waitForDataJobsApiGetReqInterceptor(3);

        this.waitForViewToRenderShort();

        return this.getPage();
    }

    tryGetWidgetsComponent() {
        return cy.get('[data-cy="get-started-widgets-component"]');
    }
}
