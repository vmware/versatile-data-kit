/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { GettingStartedPage } from "./getting-started.po";

export class DataJobsHealthPanelComponentPO extends GettingStartedPage {
    /**
     * ** Returns instance of the page object.
     *
     * @returns {DataJobsHealthPanelComponentPO}
     */
    static getComponent() {
        return new DataJobsHealthPanelComponentPO();
    }

    /**
     * ** Get Execution status gauge Widget.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getExecutionStatusGaugeWidget() {
        return cy.get("[data-cy=dp-data-jobs-status-gauge-widget]");
    }

    /**
     * ** Get percentage of successful executions against total from Execution status gauge Widget.
     *
     * @returns {Cypress.Chainable<number>}
     */
    getExecutionsSuccessPercentage() {
        return this.getExecutionStatusGaugeWidget()
            .should("exist")
            .find("[data-cy=dp-jobs-executions-status-gauge-widget-percentage]")
            .invoke("text")
            .invoke("replace", /%/, "")
            .then((value) => +value);
    }

    /**
     * ** Get number of failed executions from Execution status gauge Widget.
     *
     * @returns {Cypress.Chainable<number>}
     */
    getNumberOfFailedExecutions() {
        return this.getExecutionStatusGaugeWidget()
            .should("exist")
            .find("[data-cy=dp-jobs-executions-status-gauge-widget-failed]")
            .invoke("text")
            .invoke("replace", /\s\w+/, "")
            .then((value) => +value);
    }

    /**
     * ** Get number of total executions from Execution status gauge Widget.
     *
     * @returns {Cypress.Chainable<number>}
     */
    getExecutionsTotal() {
        return this.getExecutionStatusGaugeWidget()
            .should("exist")
            .find("[data-cy=dp-jobs-executions-status-gauge-widget-total]")
            .invoke("text")
            .invoke("replace", /\s\w+/, "")
            .then((value) => +value);
    }

    /**
     * ** Get Failing Data jobs Widget.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getFailingJobsWidget() {
        return cy.get("[data-cy=dp-failed-data-jobs-widget]");
    }

    /**
     * ** Get all Data jobs from Failing Data jobs Widget.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getAllFailingJobs() {
        return this.getFailingJobsWidget()
            .should("exist")
            .find("[data-cy=dp-failed-data-jobs-widget-job-name-link]");
    }

    /**
     * ** Get Most Recent Failing Data jobs executions Widget.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getMostRecentFailingJobsExecutionsWidget() {
        return cy.get("[data-cy=dp-failed-data-jobs-executions-widget]");
    }

    /**
     * ** Get all executions from Most Recent Failing Data jobs executions Widget.
     *
     * @returns {Cypress.Chainable<JQuery<HTMLElement>>}
     */
    getAllMostRecentFailingJobsExecutions() {
        return this.getMostRecentFailingJobsExecutionsWidget()
            .should("exist")
            .find(
                "[data-cy=dp-failed-data-jobs-executions-widget-job-name-link]",
            );
    }

    // Actions

    navigateToFailingJobDetails(jobName) {
        this._navigateToDataJob(this.getAllFailingJobs(), jobName, 3);
    }

    navigateToMostRecentFailingJobExecutions(jobName) {
        this._navigateToDataJob(
            this.getAllMostRecentFailingJobsExecutions(),
            jobName,
            2,
        );
    }

    /**
     * ** Navigate to Data job
     *
     * @param {Cypress.Chainable<JQuery<HTMLElement>>} chainable
     * @param {string} jobName
     * @param {number} numberOfReqToWait
     * @private
     */
    _navigateToDataJob(chainable, jobName, numberOfReqToWait = 2) {
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
            .should("exist")
            .click({ force: true });

        this.waitForBackendRequestCompletion(numberOfReqToWait);

        this.waitForViewToRender();
    }
}
