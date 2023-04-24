/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataJobsBasePO } from '../../../../application/data-jobs-base.po';

export class DataJobsManagePage extends DataJobsBasePO {
    static getPage() {
        return new DataJobsManagePage();
    }

    static navigateTo() {
        const page = super.navigateTo('[data-cy=navigation-link-manage-datajobs]');

        // this is temporary fix for test to pass
        // proper handling with other PR for e2e test stabilization
        page.waitForBackendRequestCompletion(3);

        return page;
    }

    getPageTitle() {
        return cy.get('[data-cy=data-pipelines-manage-page-main-title]');
    }

    getDataGrid() {
        return cy.get('[data-cy=data-pipelines-manage-grid]');
    }

    getDataGridCell(content, timeout) {
        return cy.get('[id^="clr-dg-row"] > .datagrid-row-scrollable > .datagrid-scrolling-cells > .ng-star-inserted').contains(new RegExp(`^\\s*${content}\\s*$`), {
            timeout: this.resolveTimeout(timeout)
        });
    }

    getDataGridRow(jobName) {
        cy.log(`Looking for Job row: ${jobName}`);

        return this.getDataGridCell(jobName).parents('clr-dg-row');
    }

    getDataGridNavigateBtn(team, job) {
        return cy.get('[data-cy=data-pipelines-manage-grid-details-link][data-job-params="' + team + ';' + job + '"]');
    }

    getDataGridSearchInput() {
        return cy.get('[data-test-id=search-input]').first();
    }

    getDataGridClearSearchButton() {
        return cy.get('[data-test-id="clear-search-btn"]').first();
    }

    searchByJobName(jobName) {
        this.getDataGridSearchInput().type(jobName);

        this.waitForBackendRequestCompletion();

        this.waitForViewToRender();
    }

    clearSearchField() {
        this.getDataGridSearchInput().should('be.visible').clear();

        this.waitForBackendRequestCompletion();

        this.waitForViewToRender();
    }

    clearSearchFieldWithButton() {
        this.getDataGridClearSearchButton().should('be.visible').click({ force: true });

        this.waitForBackendRequestCompletion();

        this.waitForViewToRender();
    }

    refreshDataGrid() {
        cy.get('[data-cy=data-pipelines-manage-refresh-btn]').click({
            force: true
        });

        this.waitForBackendRequestCompletion();

        this.waitForViewToRender();
    }

    openJobDetails(teamName, jobName) {
        this.getDataGridNavigateBtn(teamName, jobName).scrollIntoView().should('exist').click({ force: true });

        this.waitForBackendRequestCompletion();

        this.waitForViewToRenderShort();

        cy.get('[data-cy=data-pipelines-job-page]').should('be.visible');
    }

    selectRow(jobName) {
        this.getDataGridRow(jobName).find('.datagrid-select input').check({ force: true });
    }

    getExecuteNowGridButton() {
        return cy.get('[data-cy=data-pipelines-manage-grid-execute-btn]');
    }

    changeStatus(newStatus) {
        cy.get(`[data-cy=data-pipelines-job-${newStatus}-btn]`).should('exist').should('be.enabled').click({ force: true });
    }

    getJobStatus(jobName) {
        return this.getDataGridRow(jobName).then(($row) => {
            if ($row.find('[data-cy=data-pipelines-job-disabled]').length) {
                return 'disable';
            }

            if ($row.find('[data-cy=data-pipelines-job-enabled]').length) {
                return 'enable';
            }

            return 'not_deployed';
        });
    }

    toggleJobStatus(jobName) {
        this.selectRow(jobName);

        this.getJobStatus(jobName).then((currentStatus) => {
            if (currentStatus === 'not_deployed') {
                throw new Error('Data job is not Deployed.');
            }

            const newStatus = currentStatus === 'enable' ? 'disable' : 'enable';

            cy.log(`Current status: ${currentStatus}, new status: ${newStatus}`);

            this.changeStatus(newStatus);

            this.confirmInConfirmDialog(() => {
                this.waitForPatchDetailsReqInterceptor();
            });

            this.getToastTitle().should('exist').should('contain.text', 'Status update completed');

            this.getToastDismiss().should('exist').click({ force: true });

            this.waitForClickThinkingTime(); // Natural wait for User action

            this.refreshDataGrid();

            this.getJobStatus(jobName).then((changedStatus) => {
                expect(changedStatus).to.equal(newStatus);
            });
        });
    }

    filterByJobName(jobName) {
        cy.get('[data-cy=data-pipelines-jobs-name-column] > .datagrid-column-flex > clr-dg-string-filter.ng-star-inserted > clr-dg-filter > .datagrid-filter-toggle > cds-icon').click({ force: true });

        cy.get('div.datagrid-filter > input').should('be.visible').type(jobName);

        this.getPageTitle().should('be.visible').click({ force: true });

        this.waitForBackendRequestCompletion();

        this.waitForViewToRenderShort();
    }

    executeDataJob(jobName) {
        this.selectRow(jobName);

        this.waitForClickThinkingTime();

        this.getExecuteNowGridButton().should('exist').click({ force: true });

        this.waitForViewToRenderShort();

        this.confirmInConfirmDialog(() => {
            this.waitForPostExecutionCompletion();
        });
    }

    prepareAdditionalTestJob() {
        cy.prepareAdditionalTestJobs();

        this.waitForApiModifyCall();
    }
}
