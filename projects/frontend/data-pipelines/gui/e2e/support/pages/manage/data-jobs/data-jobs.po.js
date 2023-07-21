/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataJobsBasePO } from '../../base/data-pipelines/data-jobs-base.po';

export class DataJobsManagePage extends DataJobsBasePO {
    /**
     * ** Returns instance of the page object.
     *
     * @returns {DataJobsManagePage}
     */
    static getPage() {
        return new DataJobsManagePage();
    }

    /**
     * ** Navigate to page with provided nav link id through side menu navigation, choose Team, and return instance of page object.
     *
     * @return {DataJobsManagePage}
     */
    static navigateWithSideMenu() {
        return super.navigateWithSideMenu(
            'navLinkManageDataJobs',
            'openManage',
            {
                before: () => {
                    this.waitForApplicationBootstrap();
                    this.waitForDataJobsApiGetReqInterceptor(3);
                },
                after: () => {
                    this.waitForDataJobsApiGetReqInterceptor();

                    const page = this.getPage();
                    page.waitForGridToLoad(null);
                    page.waitForViewToRenderShort();
                }
            }
        );
    }

    /**
     * ** Navigate to Manage Data Jobs.
     *
     * @return {DataJobsManagePage}
     */
    static navigateTo() {
        /**
         * @type {DataJobsManagePage}
         */
        const page = super.navigateTo('manage');
        page.waitForGridToLoad(null);
        page.waitForViewToRenderShort();

        return page;
    }

    /**
     * ** Navigate to home page through URL and return instance of page object.
     * ** Do not wait for bootstrap and interceptors
     * @type {GetStartedPagePO}
     */
    static navigateToNoBootstrap() {
        /**
         * @type {DataJobsManagePage}
         */
        const page = super.navigateToNoBootstrap('manage');
        page.waitForGridToLoad(null);
        return page;
    }

    /**
     * ** Wait until Data grid is loaded.
     *
     * @param {string} contextSelector
     * @param {number} timeout
     * @returns {Cypress.Chainable<Subject>}
     */
    waitForGridToLoad(
        contextSelector,
        timeout = DataJobsBasePO.WAIT_SHORT_TASK
    ) {
        return this._waitForGridToLoad(
            'data-pipelines-manage-data-jobs',
            timeout
        );
    }

    getDataGrid() {
        return cy.get('[data-cy=data-pipelines-manage-grid]');
    }

    getDataGridNavigateBtn(team, job) {
        return cy.get(
            '[data-cy=data-pipelines-manage-grid-details-link][data-job-params="' +
                team +
                ';' +
                job +
                '"]'
        );
    }

    getDataGridRefreshButton() {
        return cy.get('[data-cy=data-pipelines-manage-refresh-btn]');
    }

    getExecuteNowGridButton() {
        return cy.get('[data-cy=data-pipelines-manage-grid-execute-btn]');
    }

    getJobStatus(jobName) {
        return this.getDataGridRowByName(jobName).then(($row) => {
            if ($row.find('[data-cy=data-pipelines-job-disabled]').length) {
                return 'disable';
            }

            if ($row.find('[data-cy=data-pipelines-job-enabled]').length) {
                return 'enable';
            }

            return 'not_deployed';
        });
    }

    // Actions

    executeDataJob(jobName) {
        this.selectRow(jobName);

        this.waitForClickThinkingTime();

        this.getExecuteNowGridButton().should('exist').click({ force: true });

        this.waitForViewToRenderShort();

        this.confirmInConfirmDialog(() => {
            this.waitForDataJobExecutionPostReqInterceptor();
        });
    }

    changeStatus(newStatus) {
        cy.get(`[data-cy=data-pipelines-job-${newStatus}-btn]`)
            .should('exist')
            .should('be.enabled')
            .click({ force: true });
    }

    toggleJobStatus(jobName) {
        this.selectRow(jobName);

        this.getJobStatus(jobName).then((currentStatus) => {
            if (currentStatus === 'not_deployed') {
                throw new Error('Data job is not Deployed.');
            }

            const newStatus = currentStatus === 'enable' ? 'disable' : 'enable';

            cy.log(
                `Current status: ${currentStatus}, new status: ${newStatus}`
            );

            this.changeStatus(newStatus);

            this.confirmInConfirmDialog(() => {
                this.waitForDataJobDeploymentPatchReqInterceptor();
            });

            this.getToastTitle()
                .should('exist')
                .should('contain.text', 'Status update completed');

            this.getToastDismiss().should('exist').click({ force: true });

            this.waitForClickThinkingTime(); // Natural wait for User action

            this.refreshDataGrid();

            this.getJobStatus(jobName).then((changedStatus) => {
                expect(changedStatus).to.equal(newStatus);
            });
        });
    }
}
