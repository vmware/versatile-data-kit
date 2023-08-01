/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

const { v4 } = require('uuid');

const { Logger } = require('./logger-helpers.plugins');

const JWT_TOKEN_REGEX = new RegExp(`([^\.]+)\.([^\.]+)\.([^\.]*)`);

const DEFAULT_TEST_ENV_VAR = 'lib';

/**
 * ** Generate UUID.
 *
 * @param {boolean} asynchronous - optional parameter if provided and true will return Promise<{uuid: string}>
 * @returns {Cypress.Chainable<{uuid: string}>|{uuid: string}}
 */
const generateUUID = (asynchronous = false) => {
    const uuid = v4();

    Logger.info(`Generated uuid ${uuid}`);

    if (asynchronous) {
        return Promise.resolve({ uuid });
    }

    return { uuid };
};

/**
 * Given the string representation of a JWT, return the fully decoded
 * version. This method does not validate the signature.
 *
 * @param {string} token The token to decode.
 * @returns {{header:string; claims:{[key: string]: any;}; signature:string;}} The decoded token.
 */
const parseJWTToken = (token) => {
    const parts = (token && token.match(JWT_TOKEN_REGEX)) || null;
    if (!parts) {
        throw new Error('Invalid JWT Format');
    }

    const rawHeader = parts[1];
    const rawBody = parts[2];
    const signature = parts[3];

    const header = JSON.parse(_toUnicodeString(rawHeader));
    const claims = JSON.parse(_toUnicodeString(rawBody));

    return {
        header,
        claims,
        signature
    };
};

/**
 * ** Apply Global Env Settings to loaded element and return it.
 *
 * @param {any} loadedElement
 * @param {string} injectedTestEnvVar
 * @param {string} injectedTestUid
 * @returns {string|object|any}
 */
const applyGlobalEnvSettings = (loadedElement, injectedTestEnvVar = null, injectedTestUid = null) => {
    const TEST_ENV_VAR = injectedTestEnvVar ?? _loadTestEnvironmentVar();
    const TEST_UID = injectedTestUid ?? _loadTestUid();

    if (typeof loadedElement === 'string') {
        return loadedElement.replace('$env-placeholder$', `${TEST_ENV_VAR}-${TEST_UID}`);
    }

    if (typeof loadedElement === 'object') {
        Object.entries(loadedElement).forEach(([key, value]) => {
            if (typeof value === 'string') {
                if (value.includes('$env-placeholder$')) {
                    value = value.replace('$env-placeholder$', `${TEST_ENV_VAR}-${TEST_UID}`);
                }

                loadedElement[key] = value;
            }

            if (typeof value === 'object') {
                loadedElement[key] = applyGlobalEnvSettings(value);
            }
        });
    }

    return loadedElement;
};

/**
 * ** Trim found arrays to N elements in provided object.
 *
 * @param {any} object
 * @param {number} numberOfArrayElements
 */
const trimArraysToNElements = (object, numberOfArrayElements) => {
    if (typeof object === 'undefined' || object === null || Number.isNaN(object)) {
        return object;
    }

    if (object instanceof Array) {
        if (object.length > numberOfArrayElements) {
            const chunk = object.slice(0, numberOfArrayElements);

            return [...chunk, `... ${object.length - numberOfArrayElements} more elements in the Array ...`];
        }

        return object;
    }

    if (typeof object === 'object') {
        Object.entries(object).forEach(([key, value]) => {
            if (object instanceof Array) {
                value = trimArraysToNElements(value, numberOfArrayElements);

                object[key] = value;
            }

            if (typeof value === 'object') {
                object[key] = trimArraysToNElements(value, numberOfArrayElements);
            }
        });
    }

    return object;
};

/**
 * Provided a string that represents a base-64 encoded unicode string,
 * convert it back to a regular DOMstring with appropriate character escaping.
 *
 * @param {string} encoded The encoded string to decode.
 * @returns {string} The decoded string.
 * @see https://developer.mozilla.org/en-US/docs/Web/API/WindowBase64/Base64_encoding_and_decoding
 * @private
 */
const _toUnicodeString = (encoded) => {
    // URL-save Base64 strings do not contain padding `=` characters, so add them.
    const missingPadding = encoded.length % 4;
    if (missingPadding !== 0) {
        encoded += '='.repeat(4 - missingPadding);
    }

    // Additional URL-safe character replacement
    encoded = encoded.replace(/-/g, '+').replace(/_/g, '/');
    return decodeURIComponent(Array.prototype.map.call(atob(encoded), _escapeMultibyteCharacter).join(''));
};

/**
 * Helper function for multibyte character serialization.
 *
 * @param {string} c The character to decode.
 * @returns {string} The serialized character.
 * @private
 */
const _escapeMultibyteCharacter = (c) => {
    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
};

/**
 * ** Load test environment variable from Machine global variables or from Cypress environment variables.
 * @returns {string}
 * @private
 */
const _loadTestEnvironmentVar = () => {
    /**
     * @type {string}
     */
    let testEnv;

    if (typeof process !== 'undefined' && process.env?.CYPRESS_test_environment) {
        testEnv = process.env.CYPRESS_test_environment;
    } else if (typeof Cypress !== 'undefined' && Cypress.env && Cypress.env('test_environment')) {
        testEnv = Cypress?.env('test_environment');
    }

    if (!testEnv) {
        Logger.info(`test_environment is not set in system env variable or Cypress env variable.`);
        Logger.debug(`Because test_environment is not explicitly set will use default: ${DEFAULT_TEST_ENV_VAR}`);

        testEnv = DEFAULT_TEST_ENV_VAR;
    }

    return testEnv;
};

const _loadTestUid = () => {
    /**
     * @type {string}
     */
    let guid;

    if (typeof process !== 'undefined' && process.env?.CYPRESS_test_guid) {
        guid = process.env.CYPRESS_test_guid;
    } else if (typeof Cypress !== 'undefined' && Cypress.env && Cypress.env('test_guid')) {
        guid = Cypress.env('test_guid');
    }

    if (!guid) {
        guid = '1a4d2540515640d3';

        Logger.info(`test_guid is not set in system env variable or Cypress env variable.`);
        Logger.debug(`Because test_guid is not explicitly set will use default constant: ${guid}`);
    }

    return guid;
};

module.exports = {
    generateUUID,
    applyGlobalEnvSettings,
    parseJWTToken,
    trimArraysToNElements
};
