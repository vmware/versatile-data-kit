/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

export class DataPipelinesBasePO {
    static API_MODIFY_CALL_TIME = 1000; // ms
    static SMART_DELAY_TIME = 200; // ms
    static CLICK_THINK_TIME = 500; // ms
    static ACTION_THINK_TIME = 750; // ms
    static VIEW_RENDER_SHORT_WAIT_TIME = 600; // ms
    static VIEW_RENDER_WAIT_TIME = 1500; // ms
    static INITIAL_PAGE_LOAD_WAIT_TIME = 2000; // ms
    static INITIAL_PAGE_LOAD_LONG_WAIT_TIME = 2500; // ms

    static getPage() {
        return new DataPipelinesBasePO();
    }

    static login() {
        return cy.login();
    }

    static navigateToUrl(url) {
        cy.visit(url);

        this.waitForBackendRequestCompletion();

        cy.wait(DataPipelinesBasePO.VIEW_RENDER_SHORT_WAIT_TIME);

        return this.getPage();
    }

    /**
     * ** Init API requests interceptor.
     */
    static initBackendRequestInterceptor() {
        cy.initBackendRequestInterceptor();
    }

    /**
     * ** Wait for API request interceptor.
     */
    static waitForBackendRequestCompletion(numberOfReqToWait = 1) {
        const thinkTimeMillis = 1000;

        for (let i = 0; i < numberOfReqToWait; i++) {
            cy.waitForBackendRequestCompletion();
        }

        cy.wait(thinkTimeMillis);
    }

    /**
     * ** Start HAR recording.
     *
     * @returns {Cypress.Chainable<undefined>}
     */
    static recordHarIfSupported() {
        return cy.recordHarIfSupported();
    }

    /**
     * ** Save recorded HAR.
     *
     * @returns {Cypress.Chainable<undefined>}
     */
    static saveHarIfSupported() {
        return cy.saveHarIfSupported();
    }

    /**
     * ** Response from changing Data Job status.
     * @param {string} teamName
     * @param {string} jobName
     * @param {boolean} status
     * @returns {Cypress.Chainable<undefined>}
     */
    static changeJobStatus(teamName, jobName, status) {
        return cy.changeDataJobEnabledStatus(teamName, jobName, status);
    }

    // Interceptors and waiting

    waitForBackendRequestCompletion(numberOfReqToWait = 1) {
        DataPipelinesBasePO.waitForBackendRequestCompletion(numberOfReqToWait);
    }

    waitForTestJobExecutionCompletion() {
        cy.waitForTestJobExecutionCompletion();
    }

    waitForApiModifyCall() {
        cy.wait(DataPipelinesBasePO.API_MODIFY_CALL_TIME);
    }

    waitForSmartDelay() {
        cy.wait(DataPipelinesBasePO.SMART_DELAY_TIME);
    }

    waitForClickThinkingTime() {
        cy.wait(DataPipelinesBasePO.CLICK_THINK_TIME);
    }

    waitForActionThinkingTime() {
        cy.wait(DataPipelinesBasePO.ACTION_THINK_TIME);
    }

    waitForViewToRenderShort() {
        cy.wait(DataPipelinesBasePO.VIEW_RENDER_SHORT_WAIT_TIME);
    }

    waitForViewToRender() {
        cy.wait(DataPipelinesBasePO.VIEW_RENDER_WAIT_TIME);
    }

    waitForInitialPageLoad() {
        cy.wait(DataPipelinesBasePO.INITIAL_PAGE_LOAD_WAIT_TIME);
    }

    /* Selectors */

    getMainTitle() {
        return cy.get('[data-cy=dp-main-title]');
    }

    getCurrentUrl() {
        return cy.url();
    }

    getToast(timeout) {
        return cy.get('vdk-toast-container vdk-toast', {
            timeout: this.resolveTimeout(timeout),
        });
    }

    getToastTitle(timeout) {
        return this.getToast(timeout).get('.toast-title');
    }

    getToastDismiss(timeout) {
        return this.getToast(timeout).get('.dismiss-bg');
    }

    getContentContainer() {
        return cy.get('div.content-container');
    }

    /* Actions */

    confirmInConfirmDialog() {
        cy.get('[data-cy=confirmation-dialog-ok-btn]')
            .should('exist')
            .click({ force: true });

        this.waitForBackendRequestCompletion();

        this.waitForViewToRender();
    }

    clickOnContentContainer() {
        this.getContentContainer().should('exist').click({ force: true });

        this.waitForSmartDelay();
    }

    resolveTimeout(timeout) {
        return timeout === undefined
            ? Cypress.config('defaultCommandTimeout')
            : timeout;
    }

    readFile(folderName, fileName) {
        const path = require('path');
        const downloadsFolder = Cypress.config(folderName);

        return cy.readFile(path.join(downloadsFolder, fileName));
    }

    clearLocalStorage(key) {
        if (key) {
            cy.clearLocalStorage(key);

            return;
        }

        cy.clearLocalStorage();
    }
}
