/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import {
    TEAM_NAME_DP,
    TEAM_NAME_DP_DATA_JOB_FAILING,
    TEAM_NAME_DP_DATA_JOB_TEST,
    TEAM_NAME_DP_DATA_JOB_TEST_V1,
    TEAM_NAME_DP_DATA_JOB_TEST_V2,
    TEAM_NAME_DP_DATA_JOB_TEST_V3,
} from "../helpers/constants.support";

import { applyGlobalEnvSettings } from "../../plugins/helpers/util-helpers.plugins";

export class DataPipelinesBasePO {
    static WAIT_AFTER_API_MODIFY_CALL = 1000; // ms
    static SMART_DELAY_TIME = 200; // ms
    static CLICK_THINK_TIME = 500; // ms
    static ACTION_THINK_TIME = 750; // ms
    static VIEW_RENDER_SHORT_WAIT_TIME = 600; // ms
    static VIEW_RENDER_WAIT_TIME = 1500; // ms
    static INITIAL_PAGE_LOAD_WAIT_TIME = 2000; // ms
    static INITIAL_PAGE_LOAD_LONG_WAIT_TIME = 2500; // ms
    static WAIT_AFTER_CLEANUP_RESOURCES = 5 * 1000; // ms (5s)
    static WAIT_BEFORE_SUITE_START = 1.5 * 1000; // ms (1.5s)
    static WAIT_LAST_TEST_FROM_SUITE = 3 * 1000; // ms (3s)
    static WAIT_SHORT_TASK = 60 * 1000; // ms (1m)
    static WAIT_MEDIUM_TASK = 3 * 60 * 1000; // ms (3m)
    static WAIT_LONG_TASK = 5 * 60 * 1000; // ms (5m)
    static WAIT_EXTRA_LONG_TASK = 10 * 60 * 1000; // ms (10m)

    // Generics

    /**
     * @returns {DataPipelinesBasePO}
     */
    static getPage() {
        return new DataPipelinesBasePO();
    }

    /**
     * ** Acquire JWT access token from CSP console API and return Chainable.
     *
     * @returns {Cypress.Chainable<undefined>}
     */
    static login() {
        return this.executeCypressCommand("login");
    }

    /**
     ** Wire user session when reattach auth cookies if exist otherwise request auth token and then set auth cookies.
     *
     * @returns {Cypress.Chainable<undefined>}
     */
    static wireUserSession() {
        return this.executeCypressCommand("wireUserSession");
    }

    /**
     * ** Init Http requests interceptors.
     */
    static initInterceptors() {
        this.executeCypressCommand("initBackendRequestInterceptor");
    }

    /**
     * ** Navigate to some url.
     *
     * @param {string} url
     */
    static navigateToUrl(url) {
        cy.visit(url);

        this.waitForBackendRequestCompletion();

        cy.wait(DataPipelinesBasePO.VIEW_RENDER_SHORT_WAIT_TIME);

        return this.getPage();
    }

    /**
     * ** Wait throttling before tests suite state.
     *
     * @returns {Cypress.Chainable<undefined>}
     */
    static waitBeforeSuiteState() {
        return cy.wait(DataPipelinesBasePO.WAIT_BEFORE_SUITE_START);
    }

    /**
     * ** Execute Cypress command.
     *
     * @param {string} cypressCommand
     * @param {number | null} numberOfExecution
     * @param {number | null} additionalWait
     * @returns {Cypress.Chainable<{context: string, action: string}>|Cypress.Chainable<undefined>}
     */
    static executeCypressCommand(
        cypressCommand,
        numberOfExecution = null,
        additionalWait = null,
    ) {
        if (typeof numberOfExecution === "number") {
            /**
             * @type Cypress.Chainable<undefined>
             */
            let lastCommand;

            for (let i = 0; i < numberOfExecution; i++) {
                lastCommand = cy[cypressCommand]();
            }

            if (typeof additionalWait === "number") {
                return cy.wait(additionalWait);
            }

            if (lastCommand) {
                return lastCommand;
            }

            return cy.wrap({
                context: "BasePagePO::base-page.po::executeCypressCommand()",
                action: "continue",
            });
        } else {
            return cy[cypressCommand]().then(($value) => {
                if (typeof additionalWait === "number") {
                    return cy.wait(additionalWait);
                }

                return $value;
            });
        }
    }

    /**
     * ** Wait for API request interceptor.
     */
    static waitForBackendRequestCompletion(numberOfReqToWait = 1) {
        return this.executeCypressCommand(
            "waitForBackendRequestCompletion",
            numberOfReqToWait,
            1000,
        );
    }

    /**
     * ** Start HAR recording.
     *
     * @returns {Cypress.Chainable<undefined>}
     */
    static recordHarIfSupported() {
        return this.executeCypressCommand("recordHarIfSupported");
    }

    /**
     * ** Save recorded HAR.
     *
     * @returns {Cypress.Chainable<undefined>}
     */
    static saveHarIfSupported() {
        return this.executeCypressCommand("saveHarIfSupported");
    }

    // Plugins invoking

    /**
     * ** Create Team in context of Data pipelines library.
     *
     * @returns {Cypress.Chainable<undefined>}
     */
    static createTeam() {
        return cy.task(
            "createTeams",
            {
                relativePathToFixtures: [`/base/teams/${TEAM_NAME_DP}.json`],
            },
            { timeout: DataPipelinesBasePO.WAIT_MEDIUM_TASK },
        );
    }

    /**
     * ** Create long-lived Data Jobs.
     *
     * @param {'failing'|'test'} instruction
     * @returns {Cypress.Chainable<undefined>}
     */
    static createLongLivedJobs(...instruction) {
        const relativePathToFixtures = [];
        if (instruction.includes("failing")) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_NAME_DP_DATA_JOB_FAILING}.json`,
                pathToZipFile: `/base/data-jobs/${TEAM_NAME_DP_DATA_JOB_FAILING}.zip`,
            });
        }

        if (instruction.includes("test")) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_NAME_DP_DATA_JOB_TEST}.json`,
                pathToZipFile: `/base/data-jobs/${TEAM_NAME_DP_DATA_JOB_TEST}.zip`,
            });
        }

        return cy.task(
            "createDeployJobs",
            {
                relativePathToFixtures,
            },
            { timeout: DataPipelinesBasePO.WAIT_EXTRA_LONG_TASK },
        );
    }

    /**
     * ** Provide two executions for long-lived Data Jobs.
     *
     * @param {'failing'|'test'} instruction
     * @returns {Cypress.Chainable<undefined>}
     */
    static provideExecutionsForLongLivedJobs(...instruction) {
        const relativePathToFixtures = [];
        if (instruction.includes("failing")) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_NAME_DP_DATA_JOB_FAILING}.json`,
            });
        }

        if (instruction.includes("test")) {
            relativePathToFixtures.push({
                pathToFixture: `/base/data-jobs/${TEAM_NAME_DP_DATA_JOB_TEST}.json`,
            });
        }

        return cy.task(
            "provideDataJobsExecutions",
            {
                relativePathToFixtures,
                executions: 2,
            },
            { timeout: DataPipelinesBasePO.WAIT_EXTRA_LONG_TASK },
        );
    }

    /**
     * ** Change long-lived Data Job status.
     *
     * @param {'failing'|'test'} instruction
     * @param {boolean} status
     * @returns {Cypress.Chainable<undefined>}
     */
    static changeLongLivedJobStatus(instruction, status) {
        let pathToFixture;
        if (instruction === "failing") {
            pathToFixture = `/base/data-jobs/${TEAM_NAME_DP_DATA_JOB_FAILING}.json`;
        } else {
            pathToFixture = `/base/data-jobs/${TEAM_NAME_DP_DATA_JOB_TEST}.json`;
        }

        return cy.task(
            "changeJobsStatusesFixtures",
            {
                relativePathToFixtures: [
                    {
                        pathToFixture,
                    },
                ],
                status,
            },
            { timeout: DataPipelinesBasePO.WAIT_LONG_TASK },
        );
    }

    /**
     * ** Create base short-lived test jobs.
     *
     *      - They won't be deployed
     *      - They are created during tests execution and are deleted before and after test suits.
     *      - Executed in context of test environment.
     *
     * @returns {Cypress.Chainable<unknown>}
     */
    static createShortLivedTestJobs() {
        return cy.task(
            "createDeployJobs",
            {
                relativePathToFixtures: [
                    {
                        pathToFixture: `/base/data-jobs/short-lived/${TEAM_NAME_DP_DATA_JOB_TEST_V1}.json`,
                    },
                    {
                        pathToFixture: `/base/data-jobs/short-lived/${TEAM_NAME_DP_DATA_JOB_TEST_V2}.json`,
                    },
                ],
            },
            { timeout: DataPipelinesBasePO.WAIT_LONG_TASK },
        );
    }

    /**
     * ** Create additional short-lived test job.
     *
     *      - It won't be deployed
     *      - It's created during tests execution and is deleted before and after test suits.
     *      - Executed in context of test environment.
     *
     * @returns {Cypress.Chainable<unknown>}
     */
    static createAdditionalShortLivedTestJobs() {
        return cy
            .task(
                "createDeployJobs",
                {
                    relativePathToFixtures: [
                        {
                            pathToFixture: `/base/data-jobs/short-lived/${TEAM_NAME_DP_DATA_JOB_TEST_V3}.json`,
                        },
                    ],
                },
                { timeout: DataPipelinesBasePO.WAIT_LONG_TASK },
            )
            .then(() =>
                cy.wait(DataPipelinesBasePO.WAIT_AFTER_API_MODIFY_CALL),
            );
    }

    /**
     * ** Wait for Test Data Job existing execution to complete.
     */
    static waitForTestJobExecutionToComplete() {
        return this.loadLongLivedTestJobFixture().then((jobFixture) =>
            cy.task(
                "waitForDataJobExecutionToComplete",
                {
                    jobFixture,
                    jobExecutionTimeout: 180000,
                },
                { timeout: DataPipelinesBasePO.WAIT_LONG_TASK },
            ),
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
    static deleteShortLivedTestJobs() {
        return cy.task(
            "deleteJobsFixtures",
            {
                relativePathToFixtures: [
                    {
                        pathToFixture: `/base/data-jobs/short-lived/${TEAM_NAME_DP_DATA_JOB_TEST_V1}.json`,
                    },
                    {
                        pathToFixture: `/base/data-jobs/short-lived/${TEAM_NAME_DP_DATA_JOB_TEST_V2}.json`,
                    },
                    {
                        pathToFixture: `/base/data-jobs/short-lived/${TEAM_NAME_DP_DATA_JOB_TEST_V3}.json`,
                    },
                ],
            },
            { timeout: DataPipelinesBasePO.WAIT_LONG_TASK },
        );
    }

    /**
     * ** Load long-lived test Data Job fixture.
     *
     * @returns {Cypress.Chainable<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>}
     */
    static loadLongLivedTestJobFixture() {
        return cy
            .fixture(`/base/data-jobs/${TEAM_NAME_DP_DATA_JOB_TEST}.json`)
            .then((fixture) => applyGlobalEnvSettings(fixture));
    }

    /**
     * ** Load long-lived failing Data Job fixture.
     *
     * @returns {Cypress.Chainable<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>}
     */
    static loadLongLivedFailingJobFixture() {
        return cy
            .fixture(`/base/data-jobs/${TEAM_NAME_DP_DATA_JOB_FAILING}.json`)
            .then((fixture) => applyGlobalEnvSettings(fixture));
    }

    /**
     * ** Load short-lived test Data Jobs fixture.
     *
     * @returns {Cypress.Chainable<Array<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>>}
     */
    static loadShortLivedTestJobsFixture() {
        return cy
            .fixture(
                `/base/data-jobs/short-lived/${TEAM_NAME_DP_DATA_JOB_TEST_V1}.json`,
            )
            .then((fixture1) => {
                return cy
                    .fixture(
                        `/base/data-jobs/short-lived/${TEAM_NAME_DP_DATA_JOB_TEST_V2}.json`,
                    )
                    .then((fixture2) => {
                        return cy
                            .fixture(
                                `/base/data-jobs/short-lived/${TEAM_NAME_DP_DATA_JOB_TEST_V3}.json`,
                            )
                            .then((fixture3) => {
                                return [
                                    applyGlobalEnvSettings(fixture1),
                                    applyGlobalEnvSettings(fixture2),
                                    applyGlobalEnvSettings(fixture3),
                                ];
                            });
                    });
            });
    }

    // Interceptors and waiting

    /**
     * ** Wait for API request interceptor.
     */
    waitForBackendRequestCompletion(numberOfReqToWait = 1) {
        DataPipelinesBasePO.waitForBackendRequestCompletion(numberOfReqToWait);
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
        return cy.get("[data-cy=dp-main-title]");
    }

    getCurrentUrl() {
        return cy.url();
    }

    getToast(timeout) {
        return cy.get("vmw-toast-container vmw-toast", {
            timeout: this.resolveTimeout(timeout),
        });
    }

    getToastTitle(timeout) {
        return this.getToast(timeout).get(".toast-title");
    }

    getToastDismiss(timeout) {
        return this.getToast(timeout).get(".dismiss-bg");
    }

    getContentContainer() {
        return cy.get("div.content-container");
    }

    /* Actions */

    confirmInConfirmDialog() {
        cy.get("[data-cy=confirmation-dialog-ok-btn]")
            .should("exist")
            .click({ force: true });

        this.waitForBackendRequestCompletion();

        this.waitForViewToRender();
    }

    clickOnContentContainer() {
        this.getContentContainer().should("exist").click({ force: true });

        this.waitForSmartDelay();
    }

    resolveTimeout(timeout) {
        return timeout === undefined
            ? Cypress.config("defaultCommandTimeout")
            : timeout;
    }

    readFile(folderName, fileName) {
        const path = require("path");
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
