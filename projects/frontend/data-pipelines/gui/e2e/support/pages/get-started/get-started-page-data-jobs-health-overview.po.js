/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataPipelinesBasePO } from '../base/data-pipelines/data-pipelines-base.po';

export class GetStartedDataJobsHealthOverviewWidgetPO extends DataPipelinesBasePO {
    /**
     * ** Returns instance of the page object.
     *
     * @returns {GetStartedDataJobsHealthOverviewWidgetPO}
     */
    static getPage() {
        return new GetStartedDataJobsHealthOverviewWidgetPO();
    }

    /**
     * ** Navigate to home page through URL and return instance of page object.
     *
     * @type {GetStartedDataJobsHealthOverviewWidgetPO}
     */
    static navigateTo() {
        cy.visit('/get-started');

        this.waitForApplicationBootstrap();
        this.waitForDataJobsApiGetReqInterceptor(3);

        this.waitForViewToRenderShort();

        return this.getPage();
    }

    /**
     * ** Get Data jobs health panel.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getDataJobsHealthPanel() {
        return cy.get('[data-cy=dp-data-jobs-health-panel]');
    }

    /**
     * ** Get Execution status gauge Widget.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getExecutionStatusGaugeWidget() {
        return this.getDataJobsHealthPanel().should('exist').find('lib-widget-execution-status-gauge');
    }

    /**
     * ** Get percentage of successful executions against total from Execution status gauge Widget.
     *
     * @returns {Cypress.Chainable<number>}
     */
    getExecutionsSuccessPercentage() {
        return this.getExecutionStatusGaugeWidget()
            .should('exist')
            .find('[data-cy=dp-jobs-executions-status-gauge-widget-percentage]')
            .invoke('text')
            .invoke('trim')
            .invoke('replace', /%/, '')
            .then((value) => +value);
    }

    /**
     * ** Get number of failed executions from Execution status gauge Widget.
     *
     * @returns {Cypress.Chainable<number>}
     */
    getNumberOfFailedExecutions() {
        return this.getExecutionStatusGaugeWidget()
            .should('exist')
            .find('.value-current')
            .invoke('text')
            .invoke('trim')
            .invoke('replace', /\s\w+/, '')
            .then((value) => +value);
    }

    /**
     * ** Get number of total executions from Execution status gauge Widget.
     *
     * @returns {Cypress.Chainable<number>}
     */
    getExecutionsTotal() {
        return this.getExecutionStatusGaugeWidget()
            .should('exist')
            .find('[data-cy=dp-jobs-executions-status-gauge-widget-total]')
            .invoke('text')
            .invoke('trim')
            .invoke('replace', /\s\w+/, '')
            .then((value) => +value);
    }

    /**
     * ** Get Failing Data jobs Widget.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getFailingJobsWidget() {
        return this.getDataJobsHealthPanel().should('exist').find('lib-data-jobs-failed-widget');
    }

    /**
     * ** Get all Data jobs from Failing Data jobs Widget.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getAllFailingJobs() {
        return this.getFailingJobsWidget().should('exist').find('clr-dg-row clr-dg-cell.job-name-column');
    }

    /**
     * ** Get all Data jobs links from Failing Data jobs Widget.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getAllFailingJobsLinks() {
        return this.getFailingJobsWidget().should('exist').find('[data-cy=dp-failed-data-jobs-widget-job-name-link]');
    }

    /**
     * ** Get Most Recent Failing Data jobs Widget.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getMostRecentFailingJobsWidget() {
        return this.getDataJobsHealthPanel().should('exist').find('lib-data-jobs-executions-widget');
    }

    /**
     * ** Get all Data jobs from Most Recent Failing Data jobs Widget.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getAllMostRecentFailingJobs() {
        return this.getMostRecentFailingJobsWidget().should('exist').find('clr-dg-row clr-dg-cell.job-name-column');
    }

    /**
     * ** Get all executions from Most Recent Failing Data jobs executions Widget.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getAllMostRecentFailingJobsLinks() {
        return this.getMostRecentFailingJobsWidget().should('exist').find('[data-cy=dp-failed-data-jobs-executions-widget-job-name-link]');
    }

    // Actions

    navigateToFailingJobDetails(jobName) {
        this._navigateToDataJob(this.getAllFailingJobsLinks(), jobName, 4);
    }

    navigateToMostRecentFailingJobExecutions(jobName) {
        this._navigateToDataJob(this.getAllMostRecentFailingJobsLinks(), jobName, 3);
    }

    /**
     * ** Navigate to Data job
     *
     * @param {Cypress.Chainable<JQuery<HTMLElement>>} chainable
     * @param {string} jobName
     * @param {number} numberOfReqToWait
     * @private
     */
    _navigateToDataJob(chainable, jobName, numberOfReqToWait = 3) {
        chainable
            .then((elements) => {
                /**
                 * @type {HTMLElement}
                 */
                let foundElement;
                elements.each((_index, el) => {
                    if (el.innerText.trim().includes(jobName)) {
                        foundElement = el;

                        return false;
                    }
                });

                return foundElement;
            })
            .should('exist')
            .click({ force: true });

        this.waitForDataJobsApiGetReqInterceptor(numberOfReqToWait);

        this.waitForViewToRender();
    }
}
