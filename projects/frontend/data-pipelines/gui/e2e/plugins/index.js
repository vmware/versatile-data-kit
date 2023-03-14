/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />
// ***********************************************************
// This example plugins/index.js can be used to load plugins
//
// You can change the location of this file or turn off loading
// the plugins file with the 'pluginsFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/plugins-guide
// ***********************************************************

// This function is called when a project is opened or re-opened (e.g. due to
// the project's config changing)

const path = require("path");

const {
    install,
    ensureBrowserFlags,
} = require("@neuralegion/cypress-har-generator");

const { generateUUID } = require("./helpers/util-helpers.plugins");

const {
    getAccessTokenAsynchronous,
    setAccessTokenAsynchronous,
    getAccessTokenSynchronous,
} = require("./helpers/authentication-helpers.plugins");

const {
    createTeams,
    deleteTeam,
    createUpdateTeam,
    generateRandomTeams,
} = require("./helpers/team-helpers.plugins");

const {
    createDeployJobs,
    provideDataJobsExecutions,
    waitForDataJobExecutionToComplete,
    deleteJobs,
    deleteJobsFixtures,
    changeJobsStatusesFixtures,
} = require("./helpers/job-helpers.plugins");

const { deployLineageData } = require("./helpers/lineage-helpers.plugins");

/**
 * @type {Cypress.PluginConfig}
 */
// eslint-disable-next-line no-unused-vars
// `cypressConfig` is the resolved Cypress config
module.exports = (on, cypressConfig) => {
    const TASKS = {
        /**
         * ** Create/Update Team.
         *
         * @param {{fixture: {name: string; description: string; users: Array<{id: string; description: string}>; lakeNamespaces: Array<string>; collectors:Array<string>}; forceUpdateIfExist: boolean}} taskConfig
         * @returns {Promise<{fixture: {name: string, users: Array<{id: string, description: string}>, lakeNamespaces: Array<string>, collectors: Array<string>}}>}
         */
        createUpdateTeam: (taskConfig) => {
            return createUpdateTeam(
                {
                    ...taskConfig,
                },
                { ...cypressConfig },
            );
        },
        /**
         * ** Create Teams if not exist.
         *
         * @param {{relativePathToFixtures: string[]}} taskConfig - configuration for task.
         *      relativePathToFixtures provides relative paths for fixtures files starting from directory fixtures
         *      e.g. {
         *             relativePathToFixtures: [
         *                  '/base/teams/cy-e2e-team-z-dp-lib.json'
         *             ]
         *           }
         * @returns {Promise<boolean>}
         */
        createTeams: (taskConfig) => {
            return createTeams(
                {
                    ...taskConfig,
                    forceUpdateIfExist: false,
                },
                { ...cypressConfig },
            );
        },
        /**
         * ** Create/Update Teams.
         *
         * @param {{relativePathToFixtures: string[]}} taskConfig - configuration for task.
         *      relativePathToFixtures provides relative paths for fixtures files starting from directory fixtures
         *      e.g. {
         *             relativePathToFixtures: [
         *                  '/base/teams/cy-e2e-team-z-dp-lib.json'
         *             ]
         *           }
         * @returns {Promise<boolean>}
         */
        createUpdateTeams: (taskConfig) => {
            return createTeams(
                {
                    ...taskConfig,
                    forceUpdateIfExist: true,
                },
                { ...cypressConfig },
            );
        },
        /**
         * ** Generate Random Teams.
         *
         * @param {{uuid: string; numberOfTeams: number}} taskConfig
         * @returns {Promise<Array<{name: string, users: Array<{id: string, description: string}>, lakeNamespaces: Array<string>, collectors: Array<string>}>>}
         */
        generateRandomTeams: (taskConfig) => {
            return generateRandomTeams({ ...taskConfig }, { ...cypressConfig });
        },
        /**
         * ** Delete Team.
         *
         * @param {{teamFixture: {name: string; description: string; users: Array<{id: string; description: string}>; lakeNamespaces: Array<string>; collectors:Array<string>}; failOnError: boolean;}} taskConfig - configuration for task.
         * @returns {Promise<{teamFixture: {name: string; users: Array<{id: string; description: string}>; lakeNamespaces: Array<string>; collectors:Array<string>}}>}
         */
        deleteTeam: (taskConfig) => {
            return deleteTeam({ ...taskConfig }, { ...cypressConfig });
        },
        /**
         * ** Create and Deploy Data Jobs if they don't exist.
         *
         * @param {{relativePathToFixtures: Array<{pathToFixture:string; pathToZipFile?:string;}>}} taskConfig - configuration for task.
         *      relativePathToFixtures provides relative paths for fixtures files starting from directory fixtures
         *      e.g. {
         *             relativePathToFixtures: [
         *                  {
         *                      pathToFixture: '/base/data-jobs/cy-e2e-team-z-dp-lib-failing-v0.json',
         *                      pathToZipFile: '/base/data-jobs/cy-e2e-team-z-dp-lib-failing-v0.zip'
         *                  }
         *             ]
         *           }
         * @returns {Promise<boolean>}
         */
        createDeployJobs: (taskConfig) => {
            return createDeployJobs(taskConfig, { ...cypressConfig });
        },
        /**
         * ** Provide Data Jobs executions.
         *
         * @param {{relativePathToFixtures: Array<{pathToFixture:string;}>; executions?: number;}} taskConfig - configuration for task.
         *      relativePathToFixtures provides relative paths for fixtures files starting from directory fixtures
         *      e.g. {
         *             relativePathToFixtures: [
         *                  {
         *                      pathToFixture: '/base/data-jobs/cy-e2e-team-z-dp-lib-failing-v0.json'
         *                  }
         *             ],
         *             executions: 2
         *           }
         * @returns {Promise<boolean>}
         */
        provideDataJobsExecutions: (taskConfig) => {
            return provideDataJobsExecutions(taskConfig, { ...cypressConfig });
        },
        /**
         * ** Wait for Data Jobs execution for complete.
         *
         * @param {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}} jobFixture
         * @param {number} jobExecutionTimeout - job execution timeout
         * @returns {Promise<{code: number}>}
         */
        waitForDataJobExecutionToComplete: ({
            jobFixture,
            jobExecutionTimeout = 180000,
        }) => {
            return waitForDataJobExecutionToComplete(
                jobFixture,
                jobExecutionTimeout,
                { ...cypressConfig },
            );
        },
        /**
         * ** Deploy Lineage Data to MMS if not exist.
         *
         * @returns {Promise<boolean>}
         */
        deployLineageData: () => {
            return deployLineageData({ ...cypressConfig });
        },
        /**
         * ** Change Data Jobs statuses for provided fixtures.
         *
         * @param {{relativePathToFixtures: Array<{pathToFixture:string;}>; status: boolean;}} taskConfig - configuration for task.
         *      relativePathToFixtures provides relative paths for fixtures files starting from directory fixtures
         *      e.g. {
         *             relativePathToFixtures: [
         *                  {
         *                      pathToFixture: '/base/data-jobs/cy-e2e-team-z-dp-lib-failing-v0.json'
         *                  }
         *             ],
         *             status: boolean
         *           }
         * @returns {Promise<boolean>}
         */
        changeJobsStatusesFixtures: (taskConfig) => {
            return changeJobsStatusesFixtures(taskConfig, { ...cypressConfig });
        },
        /**
         * ** Delete Jobs for provided fixtures paths.
         *
         * @param {{relativePathToFixtures: Array<{pathToFixture:string;}>}} taskConfig - configuration for task.
         *      relativePathToFixtures provides relative paths for fixtures files starting from directory fixtures
         *      e.g. {
         *             relativePathToFixtures: [
         *                  {
         *                      pathToFixture: '/base/data-jobs/cy-e2e-team-z-dp-lib-failing-v0.json'
         *                  }
         *             ]
         *           }
         * @returns {Promise<boolean>}
         */
        deleteJobsFixtures: (taskConfig) => {
            return deleteJobsFixtures(taskConfig, { ...cypressConfig });
        },
        /**
         * ** Delete Data jobs if they exist.
         *
         * @param {Array<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>} jobFixtures
         * @param {Cypress.ResolvedConfigOptions} config
         * @returns {Promise<boolean>}
         */
        deleteJobs: ({ jobFixtures }) => {
            return deleteJobs(jobFixtures, { ...cypressConfig });
        },
        /**
         * ** Get JWT access token asynchronous.
         */
        getAccessToken: getAccessTokenAsynchronous,
        /**
         * ** Set JWT access token asynchronous.
         */
        setAccessToken: setAccessTokenAsynchronous,
        /**
         * ** Generate UUID.
         *
         * @returns {Cypress.Chainable<{uuid: string}>}
         */
        generateUUID: () => {
            return generateUUID(true);
        },
    };

    // `on` is used to hook into various events Cypress emits
    on("task", TASKS);

    const options = {
        outputRoot: cypressConfig.env.CYPRESS_TERMINAL_LOGS,
        // Used to trim the base path of specs and reduce nesting in the
        // generated output directory.
        specRoot: path.relative(
            cypressConfig.fileServerFolder,
            cypressConfig.integrationFolder,
        ),
        outputTarget: {
            "cypress-logs|json": "json",
        },
        printLogsToConsole: "always",
        printLogsToFile: "always",
        includeSuccessfulHookLogs: true,
        logToFilesOnAfterRun: true,
    };

    require("cypress-terminal-report/src/installLogsPrinter")(on, options);
    install(on, cypressConfig);

    on("before:browser:launch", (browser = {}, launchOptions) => {
        ensureBrowserFlags(browser, launchOptions);
        return launchOptions;
    });
};
