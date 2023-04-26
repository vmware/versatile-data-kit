/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * ** Log some value.
 *
 * @param args
 */
const consoleLog = (...args) => {
    console.log('LOG --------->', ...args);
};

/**
 * ** Log some info.
 *
 * @param args
 */
const consoleInfo = (...args) => {
    console.log('INFO -------->', ...args);
};

/**
 * ** Log some value for debugging.
 *
 * @param args
 */
const consoleDebug = (...args) => {
    console.log('DEBUG ------->', ...args);
};

/**
 * ** Log some Error.
 *
 * @param args
 */
const consoleError = (...args) => {
    console.log('ERROR ------->', ...args);
};

/**
 * ** Log profiling data like times, etc..
 *
 * @param args
 */
const consoleProfiling = (...args) => {
    console.log('PROFILING ------->', ...args);
};

module.exports = {
    Logger: {
        log: consoleLog,
        info: consoleInfo,
        debug: consoleDebug,
        error: consoleError,
        profiling: consoleProfiling
    }
};
