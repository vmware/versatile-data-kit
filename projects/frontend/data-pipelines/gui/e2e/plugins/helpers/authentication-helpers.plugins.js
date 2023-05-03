/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

let ACCESS_TOKEN;

const getAccessTokenSynchronous = () => {
    return ACCESS_TOKEN;
};

const setAccessTokenSynchronous = (token) => {
    ACCESS_TOKEN = token;

    return ACCESS_TOKEN;
};

const getAccessTokenAsynchronous = () => {
    return Promise.resolve(ACCESS_TOKEN);
};

const setAccessTokenAsynchronous = (token) => {
    ACCESS_TOKEN = token;

    return Promise.resolve(ACCESS_TOKEN);
};

module.exports = {
    getAccessTokenSynchronous,
    setAccessTokenSynchronous,
    getAccessTokenAsynchronous,
    setAccessTokenAsynchronous
};
