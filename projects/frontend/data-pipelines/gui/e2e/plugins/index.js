/*
 * Copyright 2021 VMware, Inc.
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

const { install, ensureBrowserFlags } = require('@neuralegion/cypress-har-generator');
const path = require('path');

/**
 * @type {Cypress.PluginConfig}
 */
module.exports = (on, config) => {
    const options = {
        outputRoot: config.env.CYPRESS_TERMINAL_LOGS,
        // Used to trim the base path of specs and reduce nesting in the
        // generated output directory.
        specRoot: path.relative(config.fileServerFolder, config.integrationFolder),
        outputTarget: {
            'cypress-logs|json': 'json',
        },
        printLogsToConsole: 'always',
        printLogsToFile: 'always',
        includeSuccessfulHookLogs: true,
        logToFilesOnAfterRun: true
    };

    require('cypress-terminal-report/src/installLogsPrinter')(on, options);
    install(on, config);

    on('before:browser:launch', (browser = {}, launchOptions) => {
        ensureBrowserFlags(browser, launchOptions);
        return launchOptions;
    });
};
