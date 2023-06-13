/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { GetStartedPagePO } from '../../support/pages/get-started/get-started-page.po';

describe('Get Started Page', { tags: ['@dataPipelines', '@getStarted'] }, () => {
    /**
     * @type {GetStartedPagePO}
     */
    let getStartedPage;

    before(() => {
        return GetStartedPagePO.recordHarIfSupported()
            .then(() => cy.clearLocalStorageSnapshot('get-started-page'))
            .then(() => cy.saveLocalStorage('get-started-page'))
            .then(() => {
                return cy.wrap({
                    context: 'get-started::1::get-started-page.spec::before()',
                    action: 'continue'
                });
            });
    });

    after(() => {
        return GetStartedPagePO.saveHarIfSupported().then(() =>
            cy.wrap({
                context: 'get-started::get-started-page.spec::after()',
                action: 'continue'
            })
        );
    });

    beforeEach(() => {
        cy.restoreLocalStorage('get-started-page');

        GetStartedPagePO.wireUserSession();
        GetStartedPagePO.initInterceptors();
        getStartedPage = GetStartedPagePO.navigateTo();
    });

    describe('smoke', { tags: ['@smoke'] }, () => {
        it('Main Title Component have text: Get Started with Data Pipelines', () => {
            getStartedPage.getPageTitle().invoke('text').invoke('trim').should('eq', 'Get Started with Data Pipelines');
        });
    });
});
