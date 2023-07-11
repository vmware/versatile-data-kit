/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

const { default: axios } = require('axios');

const { cloneDeep } = require('lodash');

const { Logger } = require('./logger-helpers.plugins');

const { trimArraysToNElements } = require('./util-helpers.plugins');

const { getAccessTokenSynchronous } = require('./authentication-helpers.plugins');

/**
 * ** Create Http Get request.
 *
 * @param {string} url
 * @param {Record<string, string>} headers
 * @param {{username: string; password: string}} auth
 * @returns {Promise<AxiosResponse<any>>}
 */
const httpGetReq = (url, headers = {}, auth = undefined) => {
    const startTime = new Date();

    Logger.debug(`HTTP Get request for Url =>`, url);
    Logger.profiling(`Start time: ${startTime.toISOString()}`);

    return axios
        .request({
            url,
            method: 'get',
            headers: {
                authorization: `Bearer ${getAccessTokenSynchronous()}`,
                ...headers
            },
            validateStatus: () => true,
            auth
        })
        .then((response) => {
            const endTime = new Date();

            Logger.debug(`HTTP Get response from Url with Body`, url, _filterResponseDataForDebug(response));
            Logger.profiling(`End time: ${endTime.toISOString()};`, `Duration: ${(endTime - startTime) / 1000}s`);

            return _throttle(response);
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
    const startTime = new Date();

    Logger.debug(`HTTP Post request to Url with Body =>`, url, body);
    Logger.profiling(`Start time: ${startTime.toISOString()}`);

    return axios
        .request({
            url: url,
            method: 'post',
            headers: {
                authorization: `Bearer ${getAccessTokenSynchronous()}`,
                ...headers
            },
            data: body,
            validateStatus: () => true
        })
        .then((response) => {
            const endTime = new Date();

            Logger.debug(`HTTP Post response from Url with Body`, url, _filterResponseDataForDebug(response));
            Logger.profiling(`End time: ${endTime.toISOString()};`, `Duration: ${(endTime - startTime) / 1000}s`);

            return _throttle(response);
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
    const startTime = new Date();

    Logger.debug(`HTTP Patch request to Url with Body =>`, url, body);
    Logger.profiling(`Start time: ${startTime.toISOString()}`);

    return axios
        .request({
            url: url,
            method: 'patch',
            headers: {
                authorization: `Bearer ${getAccessTokenSynchronous()}`,
                ...headers
            },
            data: body,
            validateStatus: () => true
        })
        .then((response) => {
            const endTime = new Date();

            Logger.debug(`HTTP Patch response from Url with Body`, url, _filterResponseDataForDebug(response));
            Logger.profiling(`End time: ${endTime.toISOString()};`, `Duration: ${(endTime - startTime) / 1000}s`);

            return _throttle(response);
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
    const startTime = new Date();

    Logger.debug(`HTTP Put request to Url with Body =>`, url, body);
    Logger.profiling(`Start time: ${startTime.toISOString()}`);

    return axios
        .request({
            url: url,
            method: 'put',
            headers: {
                authorization: `Bearer ${getAccessTokenSynchronous()}`,
                ...headers
            },
            data: body,
            validateStatus: () => true
        })
        .then((response) => {
            const endTime = new Date();

            Logger.debug(`HTTP Put response from Url with Body`, url, _filterResponseDataForDebug(response));
            Logger.profiling(`End time: ${endTime.toISOString()};`, `Duration: ${(endTime - startTime) / 1000}s`);

            return _throttle(response);
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
    const startTime = new Date();

    Logger.debug(`HTTP Delete request for Url =>`, url);
    Logger.profiling(`Start time: ${startTime.toISOString()}`);

    return axios
        .request({
            url: url,
            method: 'delete',
            headers: {
                authorization: `Bearer ${getAccessTokenSynchronous()}`,
                ...headers
            },
            validateStatus: () => true
        })
        .then((response) => {
            const endTime = new Date();

            Logger.debug(`HTTP Delete response from Url with Body`, url, _filterResponseDataForDebug(response));
            Logger.profiling(`End time: ${endTime.toISOString()};`, `Duration: ${(endTime - startTime) / 1000}s`);

            return _throttle(response);
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
            authorization: '... removed from logs ...'
        },
        config: {
            timeout: response.config.timeout,
            headers: {
                ...response.config.headers,
                authorization: '... removed from logs ...'
            },
            url: response.config.url,
            method: response.config.method,
            data: response.config.data
        },
        data: trimArraysToNElements(cloneDeep(response.data), 5)
    };
};

/**
 * ** Throttle responses.
 *
 * @param {Promise<AxiosResponse<any>>} response
 * @return {Promise<AxiosResponse<any>>}
 * @private
 */
const _throttle = (response) => {
    return new Promise((resolve) => {
        resolve(response); // Comment this line and uncomment bellow code if you want to test throttling in plugins api execution
        // setTimeout(() => {
        //     resolve(response);
        // }, _randomNumberBetween(2, 10) * 1000);
    });
};

/**
 * ** Generate random number between boundaries.
 *
 * @param {number} minBoundary
 * @param {number} maxBoundary
 * @return {number}
 * @private
 */
const _randomNumberBetween = (minBoundary, maxBoundary) => {
    const _min = Math.ceil(minBoundary);
    const _max = Math.ceil(maxBoundary);

    return Math.floor(Math.random() * (_max - _min + 1) + _min);
};

module.exports = {
    httpGetReq,
    httpPostReq,
    httpPatchReq,
    httpPutReq,
    httpDeleteReq
};
