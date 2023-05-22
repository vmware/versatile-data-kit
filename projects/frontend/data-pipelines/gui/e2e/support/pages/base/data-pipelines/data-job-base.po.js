/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import { DataPipelinesBasePO } from './data-pipelines-base.po';

export class DataJobBasePO extends DataPipelinesBasePO {
    /**
     * ** Returns instance of the page object.
     *
     * @returns {DataJobBasePO}
     */
    static getPage() {
        return new DataJobBasePO();
    }

    /**
     * ** Init Http requests interceptors.
     */
    static initInterceptors() {
        super.initInterceptors();

        this.executeCypressCommand('initDataJobsSingleExecutionGetReqInterceptor');
        this.executeCypressCommand('initDataJobsExecutionsGetReqInterceptor');
        this.executeCypressCommand('initDataJobPutReqInterceptor');
        this.executeCypressCommand('initDataJobDeleteReqInterceptor');
        this.executeCypressCommand('initDataJobExecutionDeleteReqInterceptor');
    }

    /**
     * ** Navigate to Data Job Url.
     *
     * @param {'explore'|'manage'} context
     * @param {string} teamName
     * @param {string} jobName
     * @param {'details'|'executions'|'lineage'} subpage
     */
    static navigateTo(context, teamName, jobName, subpage) {
        const numberOfDataJobsApiGetReqInterceptorWaiting = subpage === 'details' ? 4 : 3;

        return this.navigateToDataJobUrl(`/${context}/data-jobs/${teamName}/${jobName}/${subpage}`, numberOfDataJobsApiGetReqInterceptorWaiting);
    }

    /**
     * ** Wait for Data Job put req.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForDataJobPutReqInterceptor() {
        return this.executeCypressCommand('waitForDataJobPutReqInterceptor', 1, 1000);
    }

    /**
     * ** Wait for Data Job delete req.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForDataJobDeleteReqInterceptor() {
        return this.executeCypressCommand('waitForDataJobDeleteReqInterceptor', 1, 1000);
    }

    /**
     * ** Wait for Data Job execution delete req.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForDataJobExecutionDeleteReqInterceptor() {
        return this.executeCypressCommand('waitForDataJobExecutionDeleteReqInterceptor', 1, 1000);
    }

    /**
     * ** Wait for Data Job executions get req.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForGetExecutionsReqInterceptor() {
        return cy.wait('@dataJobsExecutionsGetReq');
    }

    /**
     * ** Wait for Data Job to not have running executions.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForDataJobToNotHaveRunningExecution() {
        cy.log('Looking if there is ongoing running execution');

        let isRunningExecution = false;

        return cy.waitForInterceptorWithRetry('@dataJobsExecutionsGetReq', 5, {
            predicate: (interception) => {
                if (interception?.response?.statusCode !== 200) {
                    return false;
                }

                const body = interception?.response?.body;
                if (body && body.data && body.data.content) {
                    if (body.data.content.length === 0 || body.data.content[0].__typename !== 'DataJobExecution') {
                        return false;
                    }

                    isRunningExecution =
                        body.data.content.findIndex((e) => {
                            if (!e || e.status === undefined) {
                                return false;
                            }

                            return e.status?.toLowerCase() === 'running' || e.status?.toLowerCase() === 'submitted';
                        }) !== -1;

                    return true;
                }

                return false;
            },
            onfulfill: () => {
                cy.log('Waiting for already running execution to stop');

                if (isRunningExecution) {
                    DataJobBasePO.waitForDataJobToFinishExecution();
                }
            }
        });
    }

    /**
     * ** Wait for Data Job to finish execution.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForDataJobToFinishExecution() {
        cy.log('Waiting execution to finish');

        return cy.waitForInterceptorWithRetry('@dataJobsSingleExecutionGetReq', 20, {
            predicate: (interception) => {
                const body = interception?.response?.body;

                return body?.status?.toLowerCase() !== 'running' && body?.status?.toLowerCase() !== 'submitted';
            }
        });
    }

    /**
     * ** Wait for Data Job execution to become canceled.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForDataJobToCancelExecution() {
        cy.log('Waiting to cancel execution');

        return cy.waitForInterceptorWithRetry('@dataJobsSingleExecutionGetReq', 20, {
            predicate: (interception) => {
                return interception?.response?.body?.status?.toLowerCase() === 'cancelled';
            }
        });
    }

    /**
     * ** Wait for response where there would be execution record with status SUBMITTED or RUNNING.
     *
     * @return {Cypress.Chainable<unknown>}
     */
    static waitForDataJobStartExecute() {
        cy.log('Waiting execution to start SUBMITTED|RUNNING');

        return cy.waitForInterceptorWithRetry('@dataJobsExecutionsGetReq', 20, {
            predicate: (interception) => {
                if (interception?.response?.statusCode !== 200) {
                    return false;
                }

                const body = interception?.response?.body;
                if (body?.data?.content?.length === 0 || body?.data?.content[0]?.__typename !== 'DataJobExecution') {
                    return false;
                }

                return (
                    body?.data?.content?.findIndex((e) => {
                        if (!e || e.status === undefined) {
                            return false;
                        }

                        return e.status?.toLowerCase() === 'running' || e.status?.toLowerCase() === 'submitted';
                    }) !== -1
                );
            }
        });
    }

    /**
     * ** Wait for response where there would be execution record with status SUBMITTED or RUNNING.
     *
     * @return {Cypress.Chainable<unknown>}
     */
    static waitForPollingToShowRunningExecution() {
        cy.log('Waiting for pooling execution with status RUNNING');

        return cy.waitForInterceptorWithRetry('@dataJobsSingleExecutionGetReq', 10, {
            predicate: (interception) => {
                const body = interception?.response?.body;
                const status = `${body?.status}`.toLowerCase();

                if (status === 'running') {
                    return true;
                } else {
                    if (status !== 'submitted') {
                        cy.log(`Execution status never changed to RUNNING, current is ${status.toUpperCase()}`);

                        return true;
                    }

                    return false;
                }
            }
        });
    }

    /**
     * ** Wait for Data Job put req.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    waitForDataJobPutReqInterceptor() {
        return DataJobBasePO.waitForDataJobPutReqInterceptor();
    }

    /**
     * ** Wait for Data Job delete req.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    waitForDataJobDeleteReqInterceptor() {
        return DataJobBasePO.waitForDataJobDeleteReqInterceptor();
    }

    /**
     * ** Wait for Data Job execution delete req.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    waitForDataJobExecutionDeleteReqInterceptor() {
        return DataJobBasePO.waitForDataJobExecutionDeleteReqInterceptor();
    }

    /**
     * ** Wait for Data Job executions get req.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    waitForGetExecutionsReqInterceptor() {
        const waitChainable = DataJobBasePO.waitForGetExecutionsReqInterceptor();
        if (waitChainable) {
            return waitChainable;
        }

        return cy.wait(500).then(() => this.waitForGetExecutionsReqInterceptor());
    }

    /* Selectors */

    getNavigateBackBtn() {
        return cy.get('[data-cy=data-pipelines-job-navigate-back]');
    }

    getExecuteNowButton() {
        return cy.get('[data-cy=data-pipelines-job-execute-btn]', {
            timeout: DataJobBasePO.WAIT_SHORT_TASK
        });
    }

    getCancelExecutionButton() {
        return cy.get('[data-cy=data-pipelines-job-cancel-execution-btn]');
    }

    getExecuteOrCancelButton() {
        return cy.get('[data-cy=data-pipelines-job-actions-container]').then(($container) => {
            if ($container && $container.length > 0) {
                const $btn = $container.find('[data-cy=data-pipelines-job-execute-btn]');

                if ($btn && $btn.length > 0) {
                    return $btn;
                }
            }

            return $container.find('[data-cy=data-pipelines-job-cancel-execution-btn]');
        });
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

    executeNow(waitToStartExecution = false) {
        this.getExecuteNowButton().should('exist').scrollIntoView().click({ force: true });

        this.confirmInConfirmDialog(() => {
            this.waitForDataJobExecutionPostReqInterceptor();
        });

        if (waitToStartExecution) {
            DataJobBasePO.waitForDataJobStartExecute();
            DataJobBasePO.waitForPollingToShowRunningExecution();
            this.waitForViewToRenderShort();
        }
    }

    cancelExecution(waitExecutionToStop = false) {
        this.getCancelExecutionButton().should('exist').scrollIntoView().click({ force: true });

        this.confirmInConfirmDialog(() => {
            this.waitForDataJobExecutionDeleteReqInterceptor();
        });

        if (waitExecutionToStop) {
            DataJobBasePO.waitForDataJobToCancelExecution();
            this.waitForViewToRenderShort();
        }
    }

    openActionDropdown() {
        this.getActionDropdownBtn().should('exist').scrollIntoView().should('be.visible').click({ force: true });

        this.waitForViewToRenderShort();
    }

    downloadJobKey() {
        this.getDownloadKeyBtn().should('exist').scrollIntoView().should('be.visible').click({ force: true });

        this.waitForDataJobsApiGetReqInterceptor();
    }

    deleteJob() {
        this.getDeleteJobBtn().scrollIntoView().should('be.visible').click({ force: true });

        this.waitForViewToRenderShort();

        this.confirmDeleteJob(() => {
            this.waitForDataJobDeleteReqInterceptor();
        });
    }

    /**
     * ** Confirm Job deletion.
     *
     * @param {() => void} interceptor
     */
    confirmDeleteJob(interceptor) {
        this.getConfirmDeleteBtn().scrollIntoView().should('be.visible').click({ force: true });

        if (interceptor) {
            interceptor();
        }
    }

    navigateBackToDataJobs() {
        this.getNavigateBackBtn().should('be.visible').click({ force: true });

        this.waitForGridDataLoad();
    }

    openDetailsTab() {
        this.getDetailsTab().should('exist').click({ force: true });

        this.waitForDataJobsApiGetReqInterceptor();
    }

    openExecutionsTab() {
        this.getExecutionsTab().should('exist').click({ force: true });

        this.waitForGridDataLoad();
    }
}
