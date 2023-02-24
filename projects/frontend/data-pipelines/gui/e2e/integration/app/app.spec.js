/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { AppPage } from '../../support/pages/app/app.po';

describe('App Page', { tags: ['@dataPipelines'] }, () => {
    before(() => {
        return AppPage.recordHarIfSupported()
                      .then(() => cy.clearLocalStorageSnapshot('app'))
                      .then(() => AppPage.login())
                      .then(() => cy.saveLocalStorage('app'));
    });

    after(() => {
        AppPage.saveHarIfSupported();
    });

    beforeEach(() => {
        cy.restoreLocalStorage('app');
    });

    it('App Page - Main Title Component have text: Data Pipelines', () => {
        AppPage.navigateTo();

        const page = AppPage.getPage();

        page
            .waitForInitialPageLoad();

        page
            .getMainTitle()
            .should('have.text', 'Data Pipelines');
    });
});
