/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * Configuration for Playwright using default from @jupyterlab/galata
 */
const baseConfig = require('@jupyterlab/galata/lib/playwright-config');

module.exports = {
  ...baseConfig,
  webServer: {
    command: 'jlpm start --allow-root',
    url: 'http://localhost:8888/lab',
    timeout: 200 * 100000,
    reuseExistingServer: !process.env.CI
  }
};
