/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

const path = require('path');

/**
 * ** Base page superclass of all page objects classes.
 */
export class BasePagePO {
    static WAIT_AFTER_API_MODIFY_CALL = 1000; // ms
    static WAIT_SMART_DELAY = 250; // ms
    static WAIT_CLICK_THINK_TIME = 500; // ms
    static WAIT_VIEW_TO_RENDER_SHORT = 600; // ms
    static WAIT_VIEW_TO_RENDER_BASE = 1000; // ms
    static WAIT_MODAL_TO_RENDER_BASE = 500; //ms
    static WAIT_ACTION_THINK_TIME = 750; // ms
    static WAIT_INITIAL_PAGE_LOAD = 2 * 1000; // ms (2s)
    static WAIT_BEFORE_SUITE_START = 1.5 * 1000; // ms (1.5s)
    static WAIT_SHORT_TASK = 60 * 1000; // ms (1m)
    static WAIT_MEDIUM_TASK = 3 * 60 * 1000; // ms (3m)
    static WAIT_LONG_TASK = 5 * 60 * 1000; // ms (5m)
    static WAIT_EXTRA_LONG_TASK = 10 * 60 * 1000; // ms (10m)

    // Generics

    /**
     * ** Acquire JWT access token from CSP console API and return Chainable.
     *
     * @returns {Cypress.Chainable<undefined>}
     */
    static login() {
        return this.executeCypressCommand('login');
    }

    /**
     ** Wire user session when reattach auth cookies if exist otherwise request auth token and then set auth cookies.
     *
     * @returns {Cypress.Chainable<undefined>}
     */
    static wireUserSession() {
        return this.executeCypressCommand('wireUserSession');
    }

    /**
     * ** Returns instance of the page object.
     */
    static getPage() {
        return new BasePagePO();
    }

    /**
     * ** Returns current browser Url.
     *
     * @param {number} timeout
     * @returns {Cypress.Chainable<string>}
     */
    static getCurrentUrl(timeout) {
        return cy.url({
            timeout: timeout ?? Cypress.config().defaultCommandTimeout
        });
    }

    /**
     * ** Init Http requests interceptors.
     */
    static initInterceptors() {
        // CSP
        this.executeCypressCommand('initCspLoggedUserProfileGetReqInterceptor');
        // Data Pipelines
        this.executeCypressCommand('initDataJobsApiGetReqInterceptor');
    }

    /**
     * ** Navigate to some url.
     *
     * @param {string} url
     * @returns {Cypress.Chainable<Cypress.AUTWindow>}
     */
    static navigateToUrl(url) {
        return cy.visit(url);
    }

    /**
     * ** Navigate to page object page url.
     */
    static navigateTo(..._args) {
        this.navigateToUrl('/');

        this.waitForApplicationBootstrap();

        return this.getPage();
    }

    /**
     * ** Navigate to page with provided nav link id through side menu navigation and return instance of page object.
     *
     * @param {string|null} navLinkId
     * @param {'openExplore'|'openManage'} sideNavCommand
     * @param {{before: () => void; after: () => void;}} interceptors
     */
    static navigateWithSideMenu(navLinkId = null, sideNavCommand = null, interceptors = null) {
        cy.visit('/');

        if (interceptors && typeof interceptors.before === 'function') {
            interceptors.before();
        } else {
            this.waitForApplicationBootstrap();
        }

        if (navLinkId) {
            const basePagePO = this.getPage();

            if (sideNavCommand === 'openExplore') {
                basePagePO.openSideMenuNavExplore();
            } else if (sideNavCommand === 'openManage') {
                basePagePO.openSideMenuNavManage();
            }

            basePagePO.navigateToPage(navLinkId);
        }

        if (interceptors && typeof interceptors.after === 'function') {
            interceptors.after();
        }

        return this.getPage();
    }

    /**
     * ** Execute Cypress command.
     *
     * @param {string} cypressCommand
     * @param {number | null} numberOfExecution
     * @param {number | null} additionalWait
     * @returns {Cypress.Chainable<{context: string, action: string}>|Cypress.Chainable<undefined>}
     */
    static executeCypressCommand(cypressCommand, numberOfExecution = null, additionalWait = null) {
        if (typeof numberOfExecution === 'number') {
            /**
             * @type Cypress.Chainable<undefined>
             */
            let lastCommand;

            for (let i = 0; i < numberOfExecution; i++) {
                lastCommand = cy[cypressCommand]();
            }

            if (typeof additionalWait === 'number') {
                return cy.wait(additionalWait);
            }

            if (lastCommand) {
                return lastCommand;
            }

            return cy.wrap({
                context: 'BasePagePO::base-page.po::executeCypressCommand()',
                action: 'continue'
            });
        } else {
            return cy[cypressCommand]().then(($value) => {
                if (typeof additionalWait === 'number') {
                    return cy.wait(additionalWait);
                }

                return $value;
            });
        }
    }

    /**
     * ** Wait for CSP logged user Get req interceptor completion.
     *
     * @param {number} additionalWait
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForCspLoggedUserProfileGetReqInterceptor(additionalWait = 1000) {
        return this.executeCypressCommand('waitForCspLoggedUserProfileGetReqInterceptor', 1, additionalWait);
    }

    /**
     * ** Wait for Data Jobs req interceptor completion.
     *
     * @param {number} numberOfReqToWait
     * @param {number} additionalWait
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForDataJobsApiGetReqInterceptor(numberOfReqToWait = 1, additionalWait = 1000) {
        return this.executeCypressCommand('waitForDataJobsApiGetReqInterceptor', numberOfReqToWait, additionalWait);
    }

    /**
     * ** Wait for Application bootstrap.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForApplicationBootstrap() {
        return this.waitForCspLoggedUserProfileGetReqInterceptor(null)
            .then(() => this.waitForViewToRenderShort())
            .then(() => this.getMainContainer().should('exist'));
    }

    /**
     * ** Wait for initial page load.
     *
     * @param {number} factor
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForInitialPageLoad(factor = 1) {
        return cy.wait(factor * BasePagePO.WAIT_INITIAL_PAGE_LOAD);
    }

    /**
     * ** Wait for View to render.
     *
     * @param {number} factor
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForViewToRender(factor = 1) {
        return cy.wait(factor * BasePagePO.WAIT_VIEW_TO_RENDER_BASE);
    }

    /**
     * ** Wait for View to render short.
     *
     * @param {number} factor
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForViewToRenderShort(factor = 1) {
        return cy.wait(factor * BasePagePO.WAIT_VIEW_TO_RENDER_SHORT);
    }

    /**
     * ** Start HAR recording.
     *
     * @returns {Cypress.Chainable<undefined>}
     */
    static recordHarIfSupported() {
        return this.executeCypressCommand('recordHarIfSupported');
    }

    /**
     * ** Save recorded HAR.
     *
     * @returns {Cypress.Chainable<undefined>}
     */
    static saveHarIfSupported() {
        return this.executeCypressCommand('saveHarIfSupported');
    }

    // Selectors

    /**
     * ** Get main container.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    static getMainContainer() {
        return cy.get('[data-automation=vdk]', {
            timeout: BasePagePO.WAIT_SHORT_TASK
        });
    }

    /**
     * ** Wait for Data Jobs req interceptor completion.
     *
     * @param {number} numberOfReqToWait
     * @return {Cypress.Chainable<undefined>}
     */
    waitForDataJobsApiGetReqInterceptor(numberOfReqToWait = 1) {
        return BasePagePO.waitForDataJobsApiGetReqInterceptor(numberOfReqToWait);
    }

    /**
     * ** Wait smart delay.
     *
     * @param {number} factor
     * @return {Cypress.Chainable<undefined>}
     */
    waitForSmartDelay(factor = 1) {
        return cy.wait(factor * BasePagePO.WAIT_SMART_DELAY); // ms
    }

    /**
     * ** Wait Initial page load to finish.
     *
     * @param {number} factor
     * @return {Cypress.Chainable<undefined>}
     */
    waitForInitialPageLoad(factor = 1) {
        return BasePagePO.waitForInitialPageLoad(factor); // ms
    }

    /**
     * ** Wait for view to render
     *
     * @param {number} factor
     * @return {Cypress.Chainable<undefined>}
     */
    waitForViewToRender(factor = 1) {
        return cy.wait(factor * BasePagePO.WAIT_VIEW_TO_RENDER_BASE); // ms
    }

    /**
     * ** Wait for view to render
     *
     * @param {number} factor
     * @return {Cypress.Chainable<undefined>}
     */
    waitForViewToRenderShort(factor = 1) {
        return cy.wait(factor * BasePagePO.WAIT_VIEW_TO_RENDER_SHORT); // ms
    }

    /**
     * ** Wait for modal to render
     *
     * @param {number} factor
     * @return {Cypress.Chainable<undefined>}
     */
    waitForModalToRender(factor = 1) {
        return cy.wait(factor * BasePagePO.WAIT_MODAL_TO_RENDER_BASE); // ms
    }

    /**
     * ** Wait before click (something like thinking time in real env).
     *
     * @param {number} factor
     * @return {Cypress.Chainable<undefined>}
     */
    waitForClickThinkingTime(factor = 1) {
        return cy.wait(factor * BasePagePO.WAIT_CLICK_THINK_TIME); // ms
    }

    /**
     * ** Wait for generic action similar to click thinking time.
     *
     * @param {number} factor
     * @return {Cypress.Chainable<undefined>}
     */
    waitForActionThinkingTime(factor = 1) {
        return cy.wait(factor * BasePagePO.WAIT_ACTION_THINK_TIME); // ms
    }

    /**
     * ** Wait until Data grid is loaded.
     *
     * @param {string} contextSelector
     * @param {number} timeout
     * @returns {Cypress.Chainable<Subject>}
     */
    waitForGridToLoad(contextSelector, timeout = BasePagePO.WAIT_SHORT_TASK) {
        return cy.get(`${contextSelector} clr-datagrid[data-automation=clr-grid-loaded]`, { timeout: this.resolveTimeout(timeout) }).should('exist');
    }

    /**
     * ** Returns current browser Url.
     *
     * @param {number} timeout
     * @returns {Cypress.Chainable<string>}
     */
    getCurrentUrl(timeout) {
        return BasePagePO.getCurrentUrl(timeout);
    }

    /**
     * ** Returns current browser Url normalized.
     *
     * @param {{includeUrl?: boolean; includeBaseUrl?: boolean; includePathSegment?: boolean; includeQueryString?: boolean; decodeQueryString?: boolean;}} extras
     * @returns {Cypress.Chainable<{pathSegment: string; queryParams: {[key: string]: string}; baseUrl?: string; url?: string}>}
     */
    getCurrentUrlNormalized(extras = { includeQueryString: true }) {
        return this.getCurrentUrl().then((locationHref) => {
            const fullUrlSplit = locationHref.split('?');
            const url = fullUrlSplit[0];
            const queryString = fullUrlSplit[1] ?? '';
            const pathSegment = url.replace(Cypress.config().baseUrl, '');

            /**
             * @type {{pathSegment: string; queryParams: {[key: string]: string}; baseUrl?: string; url?: string}}
             */
            const normalizedData = {};

            if (extras.includeBaseUrl) {
                normalizedData.baseUrl = Cypress.config().baseUrl;
            }

            if (extras.includeUrl) {
                normalizedData.url = url;
            }

            if (extras.includePathSegment) {
                normalizedData.pathSegment = `/${pathSegment.replace(/^\/+/, '')}`;
            }

            if (extras.includeQueryString) {
                normalizedData.queryParams = queryString
                    .split('&')
                    .map((queryStringChunk) => {
                        if (queryStringChunk.length === 0) {
                            return {};
                        }

                        const splitParam = queryStringChunk.split('=');

                        return {
                            [splitParam[0]]: extras.decodeQueryString ? decodeURIComponent(splitParam[1]) : splitParam[1]
                        };
                    })
                    .reduce((accumulator, currentValue) => {
                        return {
                            ...accumulator,
                            ...currentValue
                        };
                    }, {});
            }

            return cy.wrap(normalizedData);
        });
    }

    // Selectors

    /**
     * ** Get Page Title.
     *
     * @param {number | undefined | null} timeout
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getPageTitle(timeout) {
        return cy.get('[data-cy=data-pipelines-page-title]', {
            timeout: this.resolveTimeout(timeout ?? 30000)
        });
    }

    /**
     * ** Get side menu nav group btn for Explore
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getSideMenuExploreGroupBtn() {
        return cy.get('[data-cy=data-pipelines-nav-group-explore] button').should('exist').contains('Explore');
    }

    /**
     * ** Get side menu nav group btn for Manage
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getSideMenuManageGroupBtn() {
        return cy.get('[data-cy=data-pipelines-nav-group-manage] button').should('exist').contains('Manage');
    }

    /**
     * ** Get side menu navigation link with given id.
     *
     * @param {string} navLinkId
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getSideMenuNavLink(navLinkId) {
        return cy.get(`#${navLinkId} > span`);
    }

    /**
     * ** Get toast element.
     *
     * @param {number | undefined | null} timeout
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getToast(timeout) {
        return cy.get('vdk-toast-container vdk-toast', {
            timeout: this.resolveTimeout(timeout)
        });
    }

    /**
     * ** Get Toast title.
     *
     * @param {number | undefined | null} timeout
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getToastTitle(timeout) {
        return this.getToast(timeout).get('.toast-title');
    }

    /**
     * ** Get Toast dismiss button.
     *
     * @param {number | undefined | null} timeout
     * @returns {Cypress.Chainable<JQuery<HTMLButtonElement>>}
     */
    getToastDismiss(timeout) {
        return this.getToast(timeout).get('.dismiss-bg');
    }

    /**
     * ** Get Modal dialog.
     *
     * @param {number | undefined | null} timeout
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getModal(timeout) {
        return cy.get('clr-modal .modal-dialog', {
            timeout: this.resolveTimeout(timeout)
        });
    }

    /**
     * ** Get DataGrid.
     *
     *      - Override to select desired DataGrid.
     *
     * @param {string|null} contextSelector
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getGrid(contextSelector = null) {
        if (contextSelector) {
            return cy.get(`${contextSelector} clr-datagrid`);
        }

        return cy.get('clr-datagrid');
    }

    /**
     * ** Get Cell from DataGrid using the searchQuery.
     *
     * @param {string} searchQuery
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getGridCell(searchQuery) {
        return this.getGrid().contains('clr-dg-cell', searchQuery);
    }

    /**
     * ** Get Row from DataGrid using the searchQuery that identifies one of the Cells.
     *
     * @param {string} searchQuery
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getGridRow(searchQuery) {
        return this.getGridCell(searchQuery).parents('clr-dg-row');
    }

    /**
     * ** Get all Rows from DatGrid.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getGridRows() {
        return this.getGrid().find('clr-dg-row');
    }

    /**
     * ** Get select button from Row that is identified by the searchQuery.
     *
     * @param {string} searchQuery
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getGridRowSelectBtn(searchQuery) {
        return this.getGridRow(searchQuery).find('.datagrid-select input');
    }

    // Actions

    /**
     * ** Open Explore side menu nav group.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    openSideMenuNavExplore() {
        return this.getSideMenuExploreGroupBtn()
            .should('exist')
            .scrollIntoView()
            .click({ force: true })
            .then(() => this.waitForViewToRenderShort());
    }

    /**
     * ** Open Manage side menu nav group.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    openSideMenuNavManage() {
        return this.getSideMenuManageGroupBtn()
            .should('exist')
            .scrollIntoView()
            .click({ force: true })
            .then(() => this.waitForViewToRenderShort());
    }

    /**
     * ** Navigate to Manage page through link with provided id.
     *
     * @param {string} navLinkId
     * @returns {Cypress.Chainable<Subject>}
     */
    navigateToPage(navLinkId) {
        return this.getSideMenuNavLink(navLinkId).should('exist').click({ force: true });
    }

    /**
     * ** Resolve timeout using provided value or fallback to default value.
     *
     * @param {number | undefined | null} timeout
     * @returns {number}
     */
    resolveTimeout(timeout) {
        return timeout === undefined ? Cypress.config('defaultCommandTimeout') : timeout;
    }

    /**
     * ** Read file with provided name in provided directory.
     *
     * @param {string} folderName
     * @param {string} fileName
     * @returns {Cypress.Chainable<any>}
     */
    readFile(folderName, fileName) {
        const downloadsFolder = Cypress.config(folderName);

        return cy.readFile(path.join(downloadsFolder, fileName));
    }

    /**
     * ** Clear local storage key if provided, otherwise clear everything.
     *
     * @param {string | undefined | null} key
     */
    clearLocalStorage(key) {
        if (key) {
            cy.clearLocalStorage(key);

            return;
        }

        cy.clearLocalStorage();
    }

    selectGridRow(searchQuery) {
        this.getGridRowSelectBtn(searchQuery).should('exist').scrollIntoView().check({ force: true });

        this.waitForActionThinkingTime();
    }

    /**
     * ** Wait until Data grid is loaded.
     *
     * @param {'explore'|'manage'} contextSelector
     * @param {number} timeout
     * @returns {Cypress.Chainable<Subject>}
     */
    _waitForGridToLoad(contextSelector, timeout = DataJobsBasePO.WAIT_SHORT_TASK) {
        return cy.get(`[data-cy=${contextSelector}] clr-datagrid[data-automation=clr-grid-loaded]`, { timeout: this.resolveTimeout(timeout) }).should('exist');
    }
}
