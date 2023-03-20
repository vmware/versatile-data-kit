/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

const { v4 } = require("uuid");

const { Logger } = require("./logger-helpers.plugins");

const JWT_TOKEN_REGEX = new RegExp(`([^\.]+)\.([^\.]+)\.([^\.]*)`);

const DEFAULT_TEST_ENV_VAR = "lib";

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
        throw new Error("Invalid JWT Format");
    }

    const rawHeader = parts[1];
    const rawBody = parts[2];
    const signature = parts[3];

    const header = JSON.parse(_toUnicodeString(rawHeader));
    const claims = JSON.parse(_toUnicodeString(rawBody));

    return {
        header,
        claims,
        signature,
    };
};

/**
 * ** Apply Global Env Settings to loaded element and return it.
 *
 * @param {any} loadedElement
 * @param {string} injectedTestEnvVar
 * @returns {string|object|any}
 */
const applyGlobalEnvSettings = (loadedElement, injectedTestEnvVar = null) => {
    const TEST_ENV_VAR = injectedTestEnvVar ?? _loadTestEnvironmentVar();

    if (typeof loadedElement === "string") {
        return loadedElement.replace("$env-placeholder$", TEST_ENV_VAR);
    }

    if (typeof loadedElement === "object") {
        Object.entries(loadedElement).forEach(([key, value]) => {
            if (typeof value === "string") {
                if (value.includes("$env-placeholder$")) {
                    value = value.replace("$env-placeholder$", TEST_ENV_VAR);
                }

                loadedElement[key] = value;
            }

            if (typeof value === "object") {
                loadedElement[key] = applyGlobalEnvSettings(value);
            }
        });
    }

    return loadedElement;
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
        encoded += "=".repeat(4 - missingPadding);
    }

    // Additional URL-safe character replacement
    encoded = encoded.replace(/-/g, "+").replace(/_/g, "/");
    return decodeURIComponent(
        Array.prototype.map
            .call(atob(encoded), _escapeMultibyteCharacter)
            .join(""),
    );
};

/**
 * Helper function for multibyte character serialization.
 *
 * @param {string} c The character to decode.
 * @returns {string} The serialized character.
 * @private
 */
const _escapeMultibyteCharacter = (c) => {
    return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
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
    let testEnv =
        process?.env?.CYPRESS_test_environment ??
        Cypress?.env("test_environment");

    if (!testEnv) {
        console.log(
            `DataPipelines test_environment is not set. Using default: ${DEFAULT_TEST_ENV_VAR}`,
        );
        testEnv = DEFAULT_TEST_ENV_VAR;
    }

    return testEnv;
};

module.exports = {
    generateUUID,
    applyGlobalEnvSettings,
    parseJWTToken,
};
