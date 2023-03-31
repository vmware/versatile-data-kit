/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import './commands';

require('@neuralegion/cypress-har-generator/commands');
require('cypress-grep')();
require('cypress-terminal-report/src/installLogsCollector')();

Cypress.Server.defaults({
    delay: 500,
    force404: false,
    ignore: (xhr) => {
        return true;
    },
});
