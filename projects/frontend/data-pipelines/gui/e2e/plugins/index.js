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

const path = require('path');

const { install, ensureBrowserFlags } = require('@neuralegion/cypress-har-generator');

const { generateUUID } = require('./helpers/util-helpers.plugins');

const { getAccessTokenAsynchronous, setAccessTokenAsynchronous, getAccessTokenSynchronous } = require('./helpers/authentication-helpers.plugins');

const { createDeployJobs, provideDataJobsExecutions, waitForDataJobExecutionToComplete, deleteJobs, deleteJobsFixtures, changeJobsStatusesFixtures } = require('./helpers/job-helpers.plugins');

/**
 * @type {Cypress.PluginConfig}
 */
// eslint-disable-next-line no-unused-vars
// `cypressConfig` is the resolved Cypress config
module.exports = (on, cypressConfig) => {
    const TASKS = {
        /**
         * ** Create test Data Jobs if they don't exist.
         *
         * @param {{relativePathToFixtures: Array<{pathToFixture:string; pathToZipFile:string;}>}} taskConfig - configuration for task.
         *      relativePathToFixtures provides relative paths for fixtures files starting from directory fixtures
         *      e.g. {
         *             relativePathToFixtures: [
         *                  {
         *                      pathToFixture: '/base/data-jobs/cy-e2e-vdk/cy-e2e-vdk-failing-v0.json',
         *                      pathToZipFile: '/base/data-jobs/cy-e2e-vdk/cy-e2e-vdk-failing-v0.zip'
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
         *                      pathToFixture: '/base/data-jobs/cy-e2e-vdk/cy-e2e-vdk-failing-v0.json'
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
        waitForDataJobExecutionToComplete: ({ jobFixture, jobExecutionTimeout = 180000 }) => {
            return waitForDataJobExecutionToComplete(jobFixture, jobExecutionTimeout, { ...cypressConfig });
        },

        /**
         * ** Change Data Jobs statuses for provided fixtures.
         *
         * @param {{relativePathToFixtures: Array<{pathToFixture:string;}>; status: boolean;}} taskConfig - configuration for task.
         *      relativePathToFixtures provides relative paths for fixtures files starting from directory fixtures
         *      e.g. {
         *             relativePathToFixtures: [
         *                  {
         *                      pathToFixture: '/base/data-jobs/cy-e2e-vdk/cy-e2e-vdk-failing-v0.json'
         *                  }
         *             ],
         *             status: boolean
         *           }
         * @returns {Promise<boolean[]>}
         */
        changeJobsStatusesFixtures: (taskConfig) => {
            return changeJobsStatusesFixtures(taskConfig, { ...cypressConfig });
        },
        /**
         * ** Delete Jobs for provided fixtures paths.
         *
         * @param {{relativePathToFixtures: Array<{pathToFixture:string;}>; optional?: boolean;}} taskConfig - configuration for task.
         *      relativePathToFixtures provides relative paths for fixtures files starting from directory fixtures
         *      optional if set to true will instruct the plugin to not log console error, if deletion status is different from 2xx, (e.g. 404 or 500)
         *      e.g. {
         *             relativePathToFixtures: [
         *                  {
         *                      pathToFixture: '/base/data-jobs/cy-e2e-vdk/cy-e2e-vdk-failing-v0.json'
         *                  }
         *             ],
         *             optional: true
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
         * @returns {Promise<boolean[]>}
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
        }
    };

    // `on` is used to hook into various events Cypress emits
    on('task', TASKS);

    const options = {
        outputRoot: cypressConfig.env.CYPRESS_TERMINAL_LOGS,
        // Used to trim the base path of specs and reduce nesting in the
        // generated output directory.
        specRoot: path.relative(cypressConfig.fileServerFolder, cypressConfig.integrationFolder),
        outputTarget: {
            'cypress-logs|json': 'json'
        },
        printLogsToConsole: 'always',
        printLogsToFile: 'always',
        includeSuccessfulHookLogs: true,
        logToFilesOnAfterRun: true
    };

    require('cypress-terminal-report/src/installLogsPrinter')(on, options);
    install(on, cypressConfig);

    on('before:browser:launch', (browser = {}, launchOptions) => {
        ensureBrowserFlags(browser, launchOptions);
        return launchOptions;
    });
};
