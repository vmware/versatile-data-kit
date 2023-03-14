/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import "cypress-localstorage-commands";

import { parseJWTToken } from "../plugins/helpers/util-helpers.plugins";

/* returning false here prevents Cypress from failing the test */
Cypress.on("uncaught:exception", (err) => {
    // exclusive uncaught:exception suppress when it comes from Clarity Modal resize observer (ClrModalBody.addOrRemoveTabIndex)
    if (
        /Cannot read properties of null \(reading 'clientHeight'\)/.test(
            err.message,
        )
    ) {
        return false;
    }
});

let jwtToken;
let accessToken;
let expiresIn;
let idToken;
let expiresAt;

Cypress.Commands.add("login", () => {
    return cy
        .request({
            method: "POST",
            // See project README.md how to set this login url
            url: `${Cypress.env(
                "csp_url",
            )}/csp/gateway/am/api/auth/api-tokens/authorize`,
            form: true,
            body: {
                // See project README.md how to set this token
                api_token: Cypress.env("OAUTH2_API_TOKEN"),
            },
            followRedirect: false,
            failOnStatusCode: false,
        })
        .its("body")
        .then((body) => {
            let decodedAccessToken;
            try {
                decodedAccessToken = parseJWTToken(body.access_token);
            } catch (e) {
                cy.log("Failed to decode Access Token!");

                decodedAccessToken = null;
            }

            if (!decodedAccessToken || !decodedAccessToken.claims.ovl) {
                return {
                    ...body,
                    decoded_access_token: decodedAccessToken,
                };
            }

            cy.log("Requesting claims expansion");

            return cy
                .request({
                    method: "GET",
                    url: `${Cypress.env(
                        "csp_url",
                    )}/csp/gateway/am/api/auth/token/expand-overflow-claims`,
                    headers: {
                        Authorization: `Bearer ${body.access_token}`,
                    },
                })
                .its("body")
                .then((claims) => {
                    return {
                        ...body,
                        decoded_access_token: {
                            ...decodedAccessToken,
                            claims,
                        },
                    };
                });
        })
        .then((body) => {
            jwtToken = JSON.stringify(body);

            accessToken = body.access_token;
            expiresIn = body.expires_in;
            idToken = body.id_token;
            expiresAt = JSON.stringify(Date.now() + expiresIn * 1000);

            cy.task("setAccessToken", accessToken);

            window.localStorage.setItem("expires_at", expiresAt);
            window.localStorage.setItem("access_token", accessToken);
            window.localStorage.setItem("id_token", idToken);

            window.localStorage.setItem(
                `${Cypress.env("CSP_CLIENT_ID")}_oauth2_token`,
                jwtToken,
            );

            return cy.wrap({
                context: "commands::login()",
                action: "continue",
            });
        });
});

Cypress.Commands.add("wireUserSession", () => {
    if (accessToken) {
        window.localStorage.setItem(
            `${Cypress.env("CSP_CLIENT_ID")}_oauth2_token`,
            jwtToken,
        );

        window.localStorage.setItem("expires_at", expiresAt);
        window.localStorage.setItem("access_token", accessToken);
        window.localStorage.setItem("id_token", idToken);

        return cy.wrap({
            context: "commands::1::wireUserSession()",
            action: "continue",
        });
    }

    return cy.login();
});

Cypress.Commands.add("initBackendRequestInterceptor", () => {
    cy.intercept({
        method: "GET",
        url: "**/data-jobs/for-team/**",
    }).as("getJobsRequest");
});

Cypress.Commands.add("waitForBackendRequestCompletion", () => {
    cy.wait("@getJobsRequest");
});

Cypress.Commands.add("initGetExecutionsInterceptor", () => {
    cy.intercept("GET", "**/data-jobs/for-team/**", (req) => {
        if (
            req?.query?.operationName === "jobsQuery" &&
            req?.query?.query?.includes("executions")
        ) {
            req.alias = "getExecutionsRequest";
        }
    });
});

Cypress.Commands.add("initGetExecutionInterceptor", () => {
    cy.intercept({
        method: "GET",
        url: "**/data-jobs/for-team/**/executions/**",
    }).as("getExecutionRequest");
});

Cypress.Commands.add("waitForInterceptor", (aliasName, retries, predicate) => {
    cy.wait(aliasName)
        .its("response.body")
        .then((json) => {
            if (predicate(json)) {
                return;
            }

            if (retries > 0) {
                cy.waitForInterceptor(aliasName, retries - 1, predicate);
            }
        });
});

Cypress.Commands.add("initPostExecutionInterceptor", () => {
    cy.intercept({
        method: "POST",
        url: "**/data-jobs/for-team/**/executions",
    }).as("postExecuteNow");
});

Cypress.Commands.add("waitForPostExecutionCompletion", () => {
    cy.wait("@postExecuteNow");
});

Cypress.Commands.add("initDeleteExecutionInterceptor", () => {
    cy.intercept({
        method: "DELETE",
        url: "**/data-jobs/for-team/**/executions/**",
    }).as("deleteExecution");
});

Cypress.Commands.add("waitForDeleteExecutionCompletion", () => {
    cy.wait("@deleteExecution");
});

Cypress.Commands.add("recordHarIfSupported", () => {
    if (Cypress.browser.name === "chrome") {
        return cy.recordHar({
            excludePaths: [
                // exclude from dev build vendor, scripts and polyfills bundles
                /(vendor|scripts|polyfills)\.js$/,

                // exclude from dev/prod clarity styles
                /clr-ui\.min\.css$/,

                // exclude global and grafana styles
                /(styles)(\..*)?\.css$/,

                // exclude woff2 fonts
                /.*\.woff2/,

                // library js
                // exclude from prod build
                // main bundle "main.xyz.js"
                // scripts bundle "scripts.xyz.js"
                // polyfills bundle "polyfills.xyz.js"
                // runtime bundle "runtime.xyz.js"
                // lazy loaded modules "199.xyz.js"
                /(main|scripts|polyfills|runtime|\d+)(\..*)?\.js$/,
            ],
        });
    }

    return cy.wrap({
        context: "commands::recordHarIfSupported()",
        action: "continue",
    });
});

Cypress.Commands.add("saveHarIfSupported", () => {
    if (Cypress.browser.name === "chrome") {
        return cy.saveHar();
    }

    return cy.wrap({
        context: "commands::saveHarIfSupported()",
        action: "continue",
    });
});
