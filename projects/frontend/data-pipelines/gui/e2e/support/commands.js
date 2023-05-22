/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/// <reference types="cypress" />

import 'cypress-localstorage-commands';

import { parseJWTToken } from '../plugins/helpers/util-helpers.plugins';
import { BASIC_AUTH_CONFIG, CSP_ACCESS_TOKEN_KEY, CSP_EXPIRES_AT_KEY, CSP_ID_TOKEN_KEY } from './helpers/constants.support';

let jwtToken;
let idToken;
let accessToken;
let expiresAt;

/* returning false here prevents Cypress from failing the test */
// Cypress.on('uncaught:exception', (err) => {
//     // exclusive uncaught:exception suppress when it comes from Clarity Modal resize observer (ClrModalBody.addOrRemoveTabIndex)
//     if (/Cannot read properties of null \(reading 'clientHeight'\)/.test(err.message)) {
//         return false;
//     }
// });

const _persistCspDataToStorage = (payload) => {
    if (payload) {
        idToken = payload.id_token;
        accessToken = payload.access_token;
        expiresAt = JSON.stringify(Date.now() + payload.expires_in * 1000);
    }

    window.localStorage.setItem(CSP_ID_TOKEN_KEY, idToken);
    window.localStorage.setItem(CSP_ACCESS_TOKEN_KEY, accessToken);
    window.localStorage.setItem(CSP_EXPIRES_AT_KEY, expiresAt);

    // Set the CSP token in the session storage to enable the Integration testing against Management UI
    sessionStorage.setItem(CSP_ID_TOKEN_KEY, idToken);
    sessionStorage.setItem(CSP_ACCESS_TOKEN_KEY, accessToken);
    sessionStorage.setItem(CSP_EXPIRES_AT_KEY, expiresAt);
};

Cypress.Commands.add('login', () => {
    cy.log('Requesting JWT Token with refresh token');

    return cy
        .request({
            followRedirect: false,
            failOnStatusCode: false,
            method: 'POST',
            // See project README.md how to set this login url
            url: `${Cypress.env('csp_url')}/csp/gateway/am/api/auth/api-tokens/authorize`,
            form: true,
            headers: {
                // CSP staging is using CloudFront CDN that does not permit bot requests unless the below user agent is set
                'user-agent': 'csp-automation-tests'
            },
            body: {
                // See project README.md how to set this token
                api_token: Cypress.env('OAUTH2_API_TOKEN')
            }
        })
        .its('body')
        .then(($body) => {
            const decodedAccessToken = parseJWTToken($body.access_token);

            if (!decodedAccessToken.claims.ovl) {
                return {
                    ...$body,
                    decoded_access_token: decodedAccessToken
                };
            }

            cy.log('Requesting claims expansion');

            return cy
                .request({
                    method: 'GET',
                    url: `${Cypress.env('csp_url')}/csp/gateway/am/api/auth/token/expand-overflow-claims`,
                    headers: {
                        Authorization: `Bearer ${$body.access_token}`,
                        // CSP staging is using CloudFront CDN that does not permit bot requests unless the below user agent is set
                        'user-agent': 'csp-automation-tests'
                    }
                })
                .its('body')
                .then((claims) => {
                    return {
                        ...$body,
                        decoded_access_token: {
                            ...decodedAccessToken,
                            claims
                        }
                    };
                });
        })
        .then((body) => {
            jwtToken = JSON.stringify(body);

            _persistCspDataToStorage(body);

            cy.task('setAccessToken', accessToken);

            cy.log('Logged in successfully.');

            return cy.wrap({
                context: 'commands::login()',
                action: 'continue'
            });
        });
});

Cypress.Commands.add('wireUserSession', () => {
    if (jwtToken) {
        _persistCspDataToStorage();

        return cy.wrap({
            context: 'commands::1::wireUserSession()',
            action: 'continue'
        });
    }

    return cy.login();
});

Cypress.Commands.add('recordHarIfSupported', () => {
    if (Cypress.browser.name === 'chrome') {
        return cy.recordHar({
            excludePaths: [
                // exclude from dev build vendor, scripts and polyfills bundles
                /(vendor|scripts|polyfills)\.js$/,

                // exclude from dev/prod clarity styles
                /clr-ui\.min\.css$/,

                // exclude global and grafana styles
                /(styles|grafana.light)(\..*)?\.css$/,

                // exclude woff2 fonts
                /.*\.woff2/,

                // SuperCollider js
                // exclude from prod build
                // main bundle "main.xyz.js"
                // scripts bundle "scripts.xyz.js"
                // polyfills bundle "polyfills.xyz.js"
                // runtime bundle "runtime.xyz.js"
                // lazy loaded modules "199.xyz.js"
                /(main|scripts|polyfills|runtime|\d+)(\..*)?\.js$/,

                // Grafana embedded panel js
                // vendors app bundle "vendors-app.xyz.js"
                // app bundle "app.xyz.js"
                // moment-app bundle "moment-app.xyz.js"
                // angular-app bundle "angular-app.xyz.js"
                // influxdbPlugin bundle "influxdbPlugin.xyz.js"
                // SoloPanelPage bundle "SoloPanelPage.xyz.js"
                /(vendors-app|app|moment-app|angular-app|influxdbPlugin|SoloPanelPage)(\..*)?\.js$/
            ]
        });
    }

    return cy.wrap({
        context: 'commands::recordHarIfSupported()',
        action: 'continue'
    });
});

Cypress.Commands.add('saveHarIfSupported', () => {
    if (Cypress.browser.name === 'chrome') {
        return cy.saveHar();
    }

    return cy.wrap({
        context: 'commands::saveHarIfSupported()',
        action: 'continue'
    });
});

// CSP

Cypress.Commands.add('initCspLoggedUserProfileGetReqInterceptor', () => {
    return cy.intercept('GET', '**/csp/gateway/am/api/auth/token-public-key?format=jwks').as('cspLoggedUserProfileGetReq');
});

Cypress.Commands.add('waitForCspLoggedUserProfileGetReqInterceptor', () => {
    return cy.wait('@cspLoggedUserProfileGetReq');
});

// Data Pipelines

Cypress.Commands.add('initDataJobsApiGetReqInterceptor', () => {
    return cy.intercept('GET', '**/data-jobs/for-team/**').as('dataJobsApiGetReq');
});

Cypress.Commands.add('waitForDataJobsApiGetReqInterceptor', () => {
    return cy.wait('@dataJobsApiGetReq');
});

Cypress.Commands.add('initDataJobsExecutionsGetReqInterceptor', () => {
    return cy.intercept('GET', '**/data-jobs/for-team/**', (req) => {
        if (req && req.query && req.query.query && req.query.operationName === 'jobsQuery' && req.query.query.includes('executions') && req.query.query.includes('DataJobExecutionFilter') && req.query.query.includes('DataJobExecutionOrder')) {
            req.alias = 'dataJobsExecutionsGetReq';
        }

        return req;
    });
});

Cypress.Commands.add('initDataJobsSingleExecutionGetReqInterceptor', () => {
    return cy.intercept('GET', '**/data-jobs/for-team/**/executions/**').as('dataJobsSingleExecutionGetReq');
});

Cypress.Commands.add('initDataJobExecutionPostReqInterceptor', () => {
    return cy.intercept('POST', '**/data-jobs/for-team/**/executions').as('dataJobExecutionPostReq');
});

Cypress.Commands.add('waitForDataJobExecutionPostReqInterceptor', () => {
    return cy.wait('@dataJobExecutionPostReq');
});

Cypress.Commands.add('initDataJobExecutionDeleteReqInterceptor', () => {
    return cy.intercept('DELETE', '**/data-jobs/for-team/**/executions/**').as('dataJobExecutionDeleteReq');
});

Cypress.Commands.add('waitForDataJobExecutionDeleteReqInterceptor', () => {
    return cy.wait('@dataJobExecutionDeleteReq');
});

Cypress.Commands.add('initDataJobPutReqInterceptor', () => {
    return cy.intercept('PUT', '**/data-jobs/for-team/*/jobs/*').as('dataJobPutReq');
});

Cypress.Commands.add('waitForDataJobPutReqInterceptor', () => {
    return cy.wait('@dataJobPutReq');
});

Cypress.Commands.add('initDataJobDeleteReqInterceptor', () => {
    return cy.intercept('DELETE', '**/data-jobs/for-team/**/jobs/**').as('dataJobDeleteReq');
});

Cypress.Commands.add('waitForDataJobDeleteReqInterceptor', () => {
    return cy.wait('@dataJobDeleteReq');
});

Cypress.Commands.add('initDataJobDeploymentPatchReqInterceptor', () => {
    return cy.intercept('PATCH', '**/data-jobs/for-team/**/deployments/**').as('dataJobDeploymentPatchReq');
});

Cypress.Commands.add('waitForDataJobDeploymentPatchReqInterceptor', () => {
    return cy.wait('@dataJobDeploymentPatchReq');
});

// Generics

Cypress.Commands.add('waitForInterceptorWithRetry', (aliasName, retries, config) => {
    return cy.wait(aliasName).then((interception) => {
        if (config.predicate(interception)) {
            if (typeof config.onfulfill === 'function') {
                config.onfulfill(interception);
            }

            return cy.wrap(interception);
        }

        if (retries > 0) {
            return cy.waitForInterceptorWithRetry(aliasName, retries - 1, config);
        }
    });
});

// App Config
Cypress.Commands.add('appConfigInterceptorDisableExploreRoute', () => {
    cy.intercept('GET', '/assets/data/appConfig.json', {
        auth: BASIC_AUTH_CONFIG,
        ignoreRoutes: ['explore/data-jobs', 'explore/data-jobs/:team/:job'],
        ignoreComponents: ['explorePage']
    });
});
