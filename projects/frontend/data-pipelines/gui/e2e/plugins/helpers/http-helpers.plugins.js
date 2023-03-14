/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright (c) 2022-2023. VMware
 * All rights reserved.
 */

const { default: axios } = require("axios");

const { Logger } = require("./logger-helpers.plugins");

const {
    getAccessTokenSynchronous,
} = require("./authentication-helpers.plugins");

/**
 * ** Create Http Get request.
 *
 * @param {string} url
 * @param {Record<string, string>} headers
 * @param {{username: string; password: string}} auth
 * @returns {Promise<AxiosResponse<any>>}
 */
const httpGetReq = (url, headers = {}, auth = undefined) => {
    Logger.debug(`HTTP Get request for Url =>`, url);

    return axios
        .request({
            url,
            method: "get",
            headers: {
                authorization: `Bearer ${getAccessTokenSynchronous()}`,
                ...headers,
            },
            validateStatus: () => true,
            auth,
        })
        .then((response) => {
            Logger.debug(
                `HTTP Get response from Url with Body`,
                url,
                _filterResponseDataForDebug(response),
            );

            return response;
        });
};

/**
 * ** Create Http Post request.
 *
 * @param {string} url
 * @param {any} body
 * @param {Record<string, string>} headers
 * @returns {Promise<AxiosResponse<any>>}
 */
const httpPostReq = (url, body, headers = {}) => {
    Logger.debug(`HTTP Post request to Url with Body =>`, url, body);

    return axios
        .request({
            url: url,
            method: "post",
            headers: {
                authorization: `Bearer ${getAccessTokenSynchronous()}`,
                ...headers,
            },
            data: body,
            validateStatus: () => true,
        })
        .then((response) => {
            Logger.debug(
                `HTTP Post response from Url with Body`,
                url,
                _filterResponseDataForDebug(response),
            );

            return response;
        });
};

/**
 * ** Create Http Patch request.
 *
 * @param {string} url
 * @param {any} body
 * @param {Record<string, string>} headers
 * @returns {Promise<AxiosResponse<any>>}
 */
const httpPatchReq = (url, body, headers = {}) => {
    Logger.debug(`HTTP Patch request to Url with Body =>`, url, body);

    return axios
        .request({
            url: url,
            method: "patch",
            headers: {
                authorization: `Bearer ${getAccessTokenSynchronous()}`,
                ...headers,
            },
            data: body,
            validateStatus: () => true,
        })
        .then((response) => {
            Logger.debug(
                `HTTP Patch response from Url with Body`,
                url,
                _filterResponseDataForDebug(response),
            );

            return response;
        });
};

/**
 * ** Create Http Put request.
 *
 * @param {string} url
 * @param {any} body
 * @param {Record<string, string>} headers
 * @returns {Promise<AxiosResponse<any>>}
 */
const httpPutReq = (url, body, headers = {}) => {
    Logger.debug(`HTTP Put request to Url with Body =>`, url, body);

    return axios
        .request({
            url: url,
            method: "put",
            headers: {
                authorization: `Bearer ${getAccessTokenSynchronous()}`,
                ...headers,
            },
            data: body,
            validateStatus: () => true,
        })
        .then((response) => {
            Logger.debug(
                `HTTP Put response from Url with Body`,
                url,
                _filterResponseDataForDebug(response),
            );

            return response;
        });
};

/**
 * ** Create Http Delete request.
 *
 * @param {string} url
 * @param {Record<string, string>} headers
 * @returns {Promise<AxiosResponse<any>>}
 */
const httpDeleteReq = (url, headers = {}) => {
    Logger.debug(`HTTP Delete request for Url =>`, url);

    return axios
        .request({
            url: url,
            method: "delete",
            headers: {
                authorization: `Bearer ${getAccessTokenSynchronous()}`,
                ...headers,
            },
            validateStatus: () => true,
        })
        .then((response) => {
            Logger.debug(
                `HTTP Delete response from Url with Body`,
                url,
                _filterResponseDataForDebug(response),
            );

            return response;
        });
};

/**
 * ** Filter Axios response object and left only crucial fields.
 *
 * @param {AxiosResponse<any>} response
 * @returns {Record<string, any>}
 * @private
 */
const _filterResponseDataForDebug = (response) => {
    return {
        status: response.status,
        statusText: response.statusText,
        headers: {
            ...response.headers,
            authorization: "... removed from logs ...",
        },
        config: {
            timeout: response.config.timeout,
            headers: {
                ...response.config.headers,
                authorization: "... removed from logs ...",
            },
            url: response.config.url,
            method: response.config.method,
            data: response.config.data,
        },
        data: response.data,
    };
};

module.exports = {
    httpGetReq,
    httpPostReq,
    httpPatchReq,
    httpPutReq,
    httpDeleteReq,
};
