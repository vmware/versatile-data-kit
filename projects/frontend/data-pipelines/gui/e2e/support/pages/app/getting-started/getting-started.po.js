/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataPipelinesBasePO } from '../../../application/data-pipelines-base.po';

export class GettingStartedPage extends DataPipelinesBasePO {
    /**
     * ** Navigate to getting started page.
     *
     * @returns {GettingStartedPage}
     */
    static navigateTo() {
        cy.visit('/get-started');

        this.waitForBackendRequestCompletion(3);

        return this.getPage();
    }

    /**
     * ** Returns instance of the page object.
     *
     * @returns {GettingStartedPage}
     */
    static getPage() {
        return new GettingStartedPage();
    }

    // Selectors

    /**
     * ** Returns main title of getting started page.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getMainTitle() {
        return cy.get('[data-cy=getting-started-main-title]');
    }

    /**
     * ** Get Data jobs health panel.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getDataJobsHealthPanel() {
        return cy.get('[data-cy=dp-data-jobs-health-panel]');
    }
}
