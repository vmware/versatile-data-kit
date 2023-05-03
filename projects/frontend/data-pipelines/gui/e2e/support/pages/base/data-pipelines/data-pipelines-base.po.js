/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import {
    TEAM_VDK,
    TEAM_VDK_DATA_JOB_FAILING,
    TEAM_VDK_DATA_JOB_TEST_V10,
    TEAM_VDK_DATA_JOB_TEST_V11,
    TEAM_VDK_DATA_JOB_TEST_V12,
    TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V0,
    TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V1,
    TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V2
} from '../../../helpers/constants.support';

import { applyGlobalEnvSettings } from '../../../../plugins/helpers/util-helpers.plugins';

import { BasePagePO } from '../base-page.po';

export class DataPipelinesBasePO extends BasePagePO {
    // Generics

    /**
     * ** Returns instance of the page object.
     *
     * @returns {DataPipelinesBasePO}
     */
    static getPage() {
        return new DataPipelinesBasePO();
    }

    /**
     * ** Init Http requests interceptors.
     */
    static initInterceptors() {
        super.initInterceptors();

        this.executeCypressCommand('initDataJobDeploymentPatchReqInterceptor');
        this.executeCypressCommand('initDataJobExecutionPostReqInterceptor');
    }

    /**
     * ** Navigate to some url.
     *
     * @param {string} url
     * @param {number} numberOfDataJobsApiGetReqInterceptorWaiting
     */
    static navigateToDataJobUrl(
        url,
        numberOfDataJobsApiGetReqInterceptorWaiting = 1
    ) {
        this.navigateToUrl(url);

        this.waitForApplicationBootstrap();
        this.waitForDataJobsApiGetReqInterceptor(
            numberOfDataJobsApiGetReqInterceptorWaiting
        );

        return this.getPage();
    }

    /**
     * ** Wait for Data Job post execution req.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForDataJobExecutionPostReqInterceptor() {
        return this.executeCypressCommand(
            'waitForDataJobExecutionPostReqInterceptor'
        );
    }

    /**
     * ** Wait for Data Job patch deployment req.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    static waitForDataJobDeploymentPatchReqInterceptor() {
        return this.executeCypressCommand(
            'waitForDataJobDeploymentPatchReqInterceptor'
        );
    }

    // Plugins invoking

    /**
     * ** Create long-lived Data Jobs.
     *
     * @param {'failing'} instruction
     * @returns {Cypress.Chainable<undefined>}
     */
    static createLongLivedJobs(...instruction) {
        const relativePathToFixtures = [];
        if (instruction.includes('failing')) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_VDK}/${TEAM_VDK_DATA_JOB_FAILING}.json`,
                pathToZipFile: `/base/data-jobs/${TEAM_VDK}/${TEAM_VDK_DATA_JOB_FAILING}.zip`
            });
        }

        return cy.task(
            'createDeployJobs',
            {
                relativePathToFixtures
            },
            { timeout: this.WAIT_EXTRA_LONG_TASK }
        );
    }

    /**
     * ** Create base short-lived test job with deployment.
     *
     *      - They are created during tests execution and are deleted before and after test suits.
     *      - Executed in context of test environment.
     *
     * @param {'v0'|'v1'|'v2'} jobVersion
     * @returns {Cypress.Chainable<unknown>}
     */
    static createShortLivedTestJobWithDeploy(...jobVersion) {
        const relativePathToFixtures = [];
        if (jobVersion.includes('v0')) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V0}.json`,
                pathToZipFile: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V0}.zip`
            });
        }

        if (jobVersion.includes('v1')) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V1}.json`,
                pathToZipFile: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V1}.zip`
            });
        }

        if (jobVersion.includes('v2')) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V2}.json`,
                pathToZipFile: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V2}.zip`
            });
        }

        return cy.task(
            'createDeployJobs',
            {
                relativePathToFixtures
            },
            { timeout: this.WAIT_EXTRA_LONG_TASK }
        );
    }

    /**
     * ** Provide two executions for long-lived Data Jobs.
     *
     * @param {'failing'} instruction
     * @returns {Cypress.Chainable<undefined>}
     */
    static provideExecutionsForLongLivedJobs(...instruction) {
        const relativePathToFixtures = [];
        if (instruction.includes('failing')) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_VDK}/${TEAM_VDK_DATA_JOB_FAILING}.json`
            });
        }

        return cy.task(
            'provideDataJobsExecutions',
            {
                relativePathToFixtures,
                executions: 2
            },
            { timeout: DataPipelinesBasePO.WAIT_EXTRA_LONG_TASK }
        );
    }

    /**
     * ** Provide one execution for short-lived Data Job with deployment.
     *
     * @param {'v0'|'v1'|'v2'} jobVersion
     * @returns {Cypress.Chainable<undefined>}
     */
    static provideExecutionsForShortLivedTestJobWithDeploy(...jobVersion) {
        const relativePathToFixtures = [];
        if (jobVersion.includes('v0')) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V0}.json`
            });
        }

        if (jobVersion.includes('v1')) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V1}.json`
            });
        }

        if (jobVersion.includes('v2')) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V2}.json`
            });
        }

        return cy.task(
            'provideDataJobsExecutions',
            {
                relativePathToFixtures,
                executions: 1
            },
            { timeout: DataPipelinesBasePO.WAIT_EXTRA_LONG_TASK }
        );
    }

    /**
     * ** Change long-lived Data Job status.
     *
     * @param {'failing'} instruction
     * @param {boolean} status
     * @returns {Cypress.Chainable<undefined>}
     */
    static changeLongLivedJobStatus(instruction, status) {
        let pathToFixture;
        if (instruction === 'failing') {
            pathToFixture = `/base/data-jobs/${TEAM_VDK}/${TEAM_VDK_DATA_JOB_FAILING}.json`;
        }

        return cy.task(
            'changeJobsStatusesFixtures',
            {
                relativePathToFixtures: [
                    {
                        pathToFixture
                    }
                ],
                status
            },
            { timeout: DataPipelinesBasePO.WAIT_LONG_TASK }
        );
    }

    /**
     * ** Change short-lived Data Job with deployment status.
     *
     * @param {'v0'|'v1'|'v2'} jobVersion
     * @param {boolean} status
     * @returns {Cypress.Chainable<undefined>}
     */
    static changeShortLivedTestJobWithDeployStatus(jobVersion, status) {
        let jobName;

        if (jobVersion === 'v0') {
            jobName = TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V0;
        } else if (jobVersion === 'v1') {
            jobName = TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V1;
        } else if (jobVersion === 'v2') {
            jobName = TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V2;
        }

        return cy.task(
            'changeJobsStatusesFixtures',
            {
                relativePathToFixtures: [
                    {
                        pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${jobName}.json`
                    }
                ],
                status
            },
            { timeout: DataPipelinesBasePO.WAIT_LONG_TASK }
        );
    }

    /**
     * ** Create base short-lived test jobs without deployments.
     *
     *      - They won't be deployed
     *      - They are created during tests execution and are deleted before and after test suits.
     *      - Executed in context of test environment.
     *
     * @returns {Cypress.Chainable<unknown>}
     */
    static createShortLivedTestJobsNoDeploy() {
        return cy.task(
            'createDeployJobs',
            {
                relativePathToFixtures: [
                    {
                        pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_V10}.json`
                    },
                    {
                        pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_V11}.json`
                    }
                ]
            },
            { timeout: DataPipelinesBasePO.WAIT_LONG_TASK }
        );
    }

    /**
     * ** Create additional short-lived test job without deployment.
     *
     *      - It won't be deployed
     *      - It's created during tests execution and is deleted before and after test suits.
     *      - Executed in context of test environment.
     *
     * @returns {Cypress.Chainable<unknown>}
     */
    static createAdditionalShortLivedTestJobsNoDeploy() {
        return cy
            .task(
                'createDeployJobs',
                {
                    relativePathToFixtures: [
                        {
                            pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_V12}.json`
                        }
                    ]
                },
                { timeout: DataPipelinesBasePO.WAIT_LONG_TASK }
            )
            .then(() =>
                cy.wait(DataPipelinesBasePO.WAIT_AFTER_API_MODIFY_CALL)
            );
    }

    /**
     * ** Wait for Test Data Job existing execution to complete.
     *
     * @param {'v0'|'v1'|'v2'} jobVersion
     */
    static waitForShortLivedTestJobWithDeployExecutionToComplete(jobVersion) {
        return this.loadShortLivedTestJobFixtureWithDeploy(jobVersion).then(
            (jobFixture) =>
                cy.task(
                    'waitForDataJobExecutionToComplete',
                    {
                        jobFixture,
                        jobExecutionTimeout: 240000
                    },
                    { timeout: DataPipelinesBasePO.WAIT_LONG_TASK }
                )
        );
    }

    /**
     * ** Delete short-lived test jobs.
     *
     *      - They are created during tests execution and are deleted before and after test suits.
     *      - Executed in context of test environment.
     *
     * @returns {Cypress.Chainable<unknown>}
     */
    static deleteShortLivedTestJobsNoDeploy() {
        return cy.task(
            'deleteJobsFixtures',
            {
                relativePathToFixtures: [
                    {
                        pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_V10}.json`
                    },
                    {
                        pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_V11}.json`
                    },
                    {
                        pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_V12}.json`
                    }
                ]
            },
            { timeout: DataPipelinesBasePO.WAIT_LONG_TASK }
        );
    }

    /**
     * ** Delete short-lived test job with deployment.
     *
     *      - They are created during tests execution and are deleted before and after test suits.
     *      - Executed in context of test environment.
     *
     * @param {'v0'|'v1'|'v2'} jobVersion
     * @returns {Cypress.Chainable<unknown>}
     */
    static deleteShortLivedTestJobWithDeploy(...jobVersion) {
        const relativePathToFixtures = [];
        if (jobVersion.includes('v0')) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V0}.json`
            });
        }

        if (jobVersion.includes('v1')) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V1}.json`
            });
        }

        if (jobVersion.includes('v2')) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V2}.json`
            });
        }

        return cy.task(
            'deleteJobsFixtures',
            {
                relativePathToFixtures
            },
            { timeout: DataPipelinesBasePO.WAIT_LONG_TASK }
        );
    }

    /**
     * ** Load long-lived failing Data Job fixture.
     *
     * @returns {Cypress.Chainable<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>}
     */
    static loadLongLivedFailingJobFixture() {
        return cy
            .fixture(
                `/base/data-jobs/${TEAM_VDK}/${TEAM_VDK_DATA_JOB_FAILING}.json`
            )
            .then((fixture) => applyGlobalEnvSettings(fixture));
    }

    /**
     * ** Load short-lived test Data Job with deployment fixture.
     *
     * @param {'v0'|'v1'|'v2'} jobVersion
     * @returns {Cypress.Chainable<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>}
     */
    static loadShortLivedTestJobFixtureWithDeploy(jobVersion) {
        let jobName;

        if (jobVersion === 'v0') {
            jobName = TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V0;
        } else if (jobVersion === 'v1') {
            jobName = TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V1;
        } else if (jobVersion === 'v2') {
            jobName = TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V2;
        }

        return cy
            .fixture(`/base/data-jobs/${TEAM_VDK}/short-lived/${jobName}.json`)
            .then((fixture) => applyGlobalEnvSettings(fixture));
    }

    /**
     * ** Load short-lived test Data Jobs fixture.
     *
     * @returns {Cypress.Chainable<Array<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>>}
     */
    static loadShortLivedTestJobsFixtureNoDeploy() {
        return cy
            .fixture(
                `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_V10}.json`
            )
            .then((fixture1) => {
                return cy
                    .fixture(
                        `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_V11}.json`
                    )
                    .then((fixture2) => {
                        return cy
                            .fixture(
                                `/base/data-jobs/${TEAM_VDK}/short-lived/${TEAM_VDK_DATA_JOB_TEST_V12}.json`
                            )
                            .then((fixture3) => {
                                return [
                                    applyGlobalEnvSettings(fixture1),
                                    applyGlobalEnvSettings(fixture2),
                                    applyGlobalEnvSettings(fixture3)
                                ];
                            });
                    });
            });
    }

    /**
     * ** Wait for Data Job patch deployment req.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    waitForDataJobDeploymentPatchReqInterceptor() {
        return DataPipelinesBasePO.waitForDataJobDeploymentPatchReqInterceptor();
    }

    /**
     * ** Wait for Data Job patch deployment req.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    waitForDataJobExecutionPostReqInterceptor() {
        return DataPipelinesBasePO.waitForDataJobExecutionPostReqInterceptor();
    }

    /**
     * ** Wait API request to finish, then grid to load and finally additional short wait rows to be rendered.
     *
     * @return {Cypress.Chainable<undefined>}
     */
    waitForGridDataLoad() {
        return this.waitForDataJobsApiGetReqInterceptor()
            .then(() => this.waitForGridToLoad(null))
            .then(() => this.waitForViewToRenderShort());
    }

    /* Selectors */

    getContentContainer() {
        return cy.get('div.content-container');
    }

    /* Actions */

    /**
     ** Confirm action in dialog.
     *
     * @param {() => void} interceptor
     */
    confirmInConfirmDialog(interceptor) {
        cy.get('[data-cy=confirmation-dialog-ok-btn]')
            .should('exist')
            .click({ force: true });

        if (interceptor) {
            interceptor();
        }

        this.waitForViewToRenderShort();
    }

    clickOnContentContainer() {
        this.getContentContainer().should('exist').click({ force: true });

        this.waitForSmartDelay();
    }
}
