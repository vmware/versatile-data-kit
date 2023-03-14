/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright (c) 2022-2023. VMware
 * All rights reserved.
 */

/**
 * ** Log some value.
 *
 * @param args
 */
const consoleLog = (...args) => {
    console.log("LOG --------->", ...args);
};

/**
 * ** Log some info.
 *
 * @param args
 */
const consoleInfo = (...args) => {
    console.log("INFO -------->", ...args);
};

/**
 * ** Log some value for debugging.
 *
 * @param args
 */
const consoleDebug = (...args) => {
    console.log("DEBUG ------->", ...args);
};

/**
 * ** Log some Error.
 *
 * @param args
 */
const consoleError = (...args) => {
    console.log("ERROR ------->", ...args);
};

module.exports = {
    Logger: {
        log: consoleLog,
        info: consoleInfo,
        debug: consoleDebug,
        error: consoleError,
    },
};
