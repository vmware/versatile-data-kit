/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { DataPipelinesBasePO } from './data-pipelines-base.po';

export class DataJobBasePO extends DataPipelinesBasePO {
    static getPage() {
        return new DataJobBasePO();
    }

    initGetExecutionInterceptor() {
        cy.initGetExecutionInterceptor();
    }

    initGetExecutionsInterceptor() {
        cy.initGetExecutionsInterceptor();
    }

    initPostExecutionInterceptor() {
        cy.initPostExecutionInterceptor();
    }

    initDeleteExecutionInterceptor() {
        cy.initDeleteExecutionInterceptor();
    }

    waitForPostExecutionCompletion() {
        cy.waitForPostExecutionCompletion();
    }

    waitForDeleteExecutionCompletion() {
        cy.waitForDeleteExecutionCompletion();
    }

    waitForDataJobStartExecute() {
        cy.waitForInterceptor('@getExecutionsRequest', 20, (response) => {
            return response?.data?.content?.findIndex((e) => {
                return (
                    e.status?.toLowerCase() === 'running' ||
                    e.status?.toLowerCase() === 'submitted'
                );
            });
        });
    }

    waitForDataJobStopExecute() {
        cy.waitForInterceptor('@getExecutionRequest', 20, (response) => {
            return response?.status === 'cancelled';
        });
    }

    /* Selectors */

    getNavigateBackBtn() {
        return cy.get('[data-cy=data-pipelines-job-navigate-back]');
    }

    getMainTitle() {
        return cy.get('[data-cy=data-pipelines-job-main-title]');
    }

    getExecuteNowButton() {
        return cy.get('[data-cy=data-pipelines-job-execute-btn]');
    }

    getCancelExecutionButton() {
        return cy.get('[data-cy=data-pipelines-job-cancel-execution-btn]');
    }

    getConfirmDialogButton() {
        return cy.get('[data-cy="confirmation-dialog-ok-btn"]');
    }

    getActionDropdownBtn() {
        return cy.get('[data-cy=data-pipelines-job-action-dropdown-btn]');
    }

    getDownloadKeyBtn() {
        return cy.get('[data-cy=data-pipelines-job-download-btn]');
    }

    getDeleteJobBtn() {
        return cy.get('[data-cy=data-pipelines-job-delete-btn]');
    }

    getConfirmDeleteBtn() {
        return cy.get('#removeBtn');
    }

    getDetailsTab() {
        return cy.get('[data-cy=data-pipelines-job-details-tab]');
    }

    getExecutionsTab() {
        return cy.get('[data-cy=data-pipelines-job-executions-tab]');
    }

    getExecutionStatus() {
        return cy.get('[data-cy="data-pipelines-job-execution-status"]');
    }

    /* Actions */

    executeNow() {
        this.getExecuteNowButton().scrollIntoView().click({ force: true });
    }

    openActionDropdown() {
        this.getActionDropdownBtn()
            .scrollIntoView()
            .should('be.visible')
            .click({ force: true });

        this.waitForClickThinkingTime();
    }

    downloadJobKey() {
        this.getDownloadKeyBtn()
            .scrollIntoView()
            .should('be.visible')
            .click({ force: true });

        this.waitForBackendRequestCompletion();
    }

    deleteJob() {
        this.getDeleteJobBtn()
            .scrollIntoView()
            .should('be.visible')
            .click({ force: true });
    }

    confirmDeleteJob() {
        this.getConfirmDeleteBtn()
            .scrollIntoView()
            .should('be.visible')
            .click({ force: true });
    }

    navigateBackToDataJobs() {
        this.getNavigateBackBtn().should('be.visible').click({ force: true });

        this.waitForBackendRequestCompletion();
    }

    openDetailsTab() {
        this.getDetailsTab().should('exist').click({ force: true });

        this.waitForBackendRequestCompletion();
    }

    openExecutionsTab() {
        this.getExecutionsTab().should('exist').click({ force: true });

        this.waitForBackendRequestCompletion();
    }
}
