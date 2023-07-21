/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

const jestJupyterLab = require('@jupyterlab/testutils/lib/jest-config');

const esModules = [
  '@jupyterlab/',
  'lib0',
  'y\\-protocols',
  'y\\-websocket',
  'yjs'
].join('|');

const jlabConfig = jestJupyterLab(__dirname);

const {
  moduleFileExtensions,
  moduleNameMapper,
  preset,
  setupFilesAfterEnv,
  setupFiles,
  testPathIgnorePatterns,
  transform
} = jlabConfig;

module.exports = {
  moduleFileExtensions,
  moduleNameMapper,
  preset,
  setupFilesAfterEnv,
  setupFiles,
  testPathIgnorePatterns,
  transform,
  automock: false,
  testEnvironment: 'jsdom',
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/.ipynb_checkpoints/*'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['lcov', 'text'],
  globals: {
    'ts-jest': {
      tsconfig: 'tsconfig.json'
    }
  },
  testRegex: 'src/.*/.*.spec.ts[x]?$',
  transformIgnorePatterns: [`/node_modules/(?!${esModules}).+`]
};
