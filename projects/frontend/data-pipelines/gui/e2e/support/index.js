/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

// ***********************************************************
// This example support/index.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands';

require('@neuralegion/cypress-har-generator/commands');

const CYPRESS_GREP = require('cypress-grep');
const CYPRESS_TERMINAL = require('cypress-terminal-report/src/installLogsCollector');

CYPRESS_GREP();

const CYPRESS_TERMINAL_ERROR_BLACKLIST = [
    'NG0100: ExpressionChangedAfterItHasBeenCheckedError',
    '"url": "https://console-stg.cloud.vmware.com/csp/gateway/slc/api/principal/org/service-families"',
    'error loading jwks,'
];

CYPRESS_TERMINAL({
    filterLog: ([logType, message, severity]) => {
        if (logType !== 'cons:error') {
            return true;
        }

        return (
            severity !== 'error' ||
            !message ||
            !CYPRESS_TERMINAL_ERROR_BLACKLIST.some((value) =>
                message.includes(value)
            )
        );
    }
});

Cypress.Server.defaults({
    delay: 500,
    force404: false,
    ignore: (xhr) => {
        return true;
    }
});

// Alternatively you can use CommonJS syntax:
// require('./commands')
