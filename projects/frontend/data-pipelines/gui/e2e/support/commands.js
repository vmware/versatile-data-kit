/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import 'cypress-localstorage-commands';

import {
    applyGlobalEnvSettings,
    createExecutionsForJob,
    createTestJob,
    deleteTestJobIfExists,
    deployTestJobIfNotExists,
    waitForJobExecutionCompletion,
} from './helpers/commands.helpers';

Cypress.Commands.add('login', () => {
    return cy
        .request({
            method: 'POST',
            // See project README.md how to set this login url
            url: Cypress.env('login_url'),
            form: true,
            body: {
                // See project README.md how to set this token
                api_token: Cypress.env('OAUTH2_API_TOKEN'),
            },
            followRedirect: false,
            failOnStatusCode: false,
        })
        .its('body')
        .then((body) => {
            const token = body.access_token;
            const expiresIn = body.expires_in;
            const idToken = body.id_token;
            const expiresAt = JSON.stringify(Date.now() + expiresIn * 1000);

            window.localStorage.setItem('expires_at', expiresAt);
            window.localStorage.setItem('access_token', token);
            window.localStorage.setItem('id_token', idToken);

            // Set the CSP token in the session storage to enable the Integration testing against Management UI
            sessionStorage.setItem('expires_at', expiresAt);
            sessionStorage.setItem('access_token', token);
            sessionStorage.setItem('id_token', idToken);

            return cy.wrap({
                context: 'commands::login()',
                action: 'continue',
            });
        });
});

Cypress.Commands.add('initBackendRequestInterceptor', () => {
    cy.intercept({
        method: 'GET',
        url: '**/data-jobs/for-team/**',
    }).as('getJobsRequest');
});

Cypress.Commands.add('waitForBackendRequestCompletion', () => {
    cy.wait('@getJobsRequest');
});

Cypress.Commands.add('initGetExecutionsInterceptor', () => {
    cy.intercept('GET', '**/data-jobs/for-team/**', (req) => {
        if (
            req?.query?.operationName === 'jobsQuery' &&
            req?.query?.query?.includes('executions')
        ) {
            req.alias = 'getExecutionsRequest';
        }
    });
});

Cypress.Commands.add('initGetExecutionInterceptor', () => {
    cy.intercept({
        method: 'GET',
        url: '**/data-jobs/for-team/**/executions/**',
    }).as('getExecutionRequest');
});

Cypress.Commands.add('waitForInterceptor', (aliasName, retries, predicate) => {
    cy.wait(aliasName)
        .its('response.body')
        .then((json) => {
            if (predicate(json)) {
                return;
            }

            if (retries > 0) {
                cy.waitForInterceptor(aliasName, retries - 1, predicate);
            }
        });
});

Cypress.Commands.add('initPatchDetailsReqInterceptor', () => {
    cy.intercept('PATCH', '**/data-jobs/for-team/**/jobs/**/deployments/**').as(
        'patchJobDetails',
    );
});

Cypress.Commands.add('waitForPatchDetailsReqInterceptor', () => {
    cy.wait('@patchJobDetails');
});

Cypress.Commands.add('initPostExecutionInterceptor', () => {
    cy.intercept({
        method: 'POST',
        url: '**/data-jobs/for-team/**/executions',
    }).as('postExecuteNow');
});

Cypress.Commands.add('waitForPostExecutionCompletion', () => {
    cy.wait('@postExecuteNow');
});

Cypress.Commands.add('initDeleteExecutionInterceptor', () => {
    cy.intercept({
        method: 'DELETE',
        url: '**/data-jobs/for-team/**/executions/**',
    }).as('deleteExecution');
});

Cypress.Commands.add('waitForDeleteExecutionCompletion', () => {
    cy.wait('@deleteExecution');
});

Cypress.Commands.add('recordHarIfSupported', () => {
    if (Cypress.browser.name === 'chrome') {
        return cy.recordHar({
            excludePaths: [
                'vendor.js$',
                'clr-ui.min.css$',
                'scripts.js$',
                'polyfills.js$',
            ],
        });
    }

    return cy.wrap({
        context: 'commands::recordHarIfSupported()',
        action: 'continue',
    });
});

Cypress.Commands.add('saveHarIfSupported', () => {
    if (Cypress.browser.name === 'chrome') {
        return cy.saveHar();
    }

    return cy.wrap({
        context: 'commands::saveHarIfSupported()',
        action: 'continue',
    });
});

Cypress.Commands.add('prepareBaseTestJobs', () => {
    return cy.fixture('lib/explore/test-jobs.json').then((testJobs) => {
        return Promise.all(
            testJobs.map((testJob) => {
                const normalizedTestJob = applyGlobalEnvSettings(testJob);

                return createTestJob(normalizedTestJob);
            }),
        );
    });
});

Cypress.Commands.add('prepareAdditionalTestJobs', () => {
    return cy
        .fixture('lib/explore/additional-test-job.json')
        .then((testJob) => {
            const normalizedTestJob = applyGlobalEnvSettings(testJob);

            return createTestJob(normalizedTestJob);
        });
});

Cypress.Commands.add('prepareLongLivedTestJob', () => {
    return deployTestJobIfNotExists(
        'lib/manage/e2e-cypress-dp-test.json',
        'lib/manage/e2e-cypress-dp-test.zip',
    );
});

Cypress.Commands.add('prepareLongLivedFailingTestJob', () => {
    return deployTestJobIfNotExists(
        'e2e-cy-dp-failing.job.json',
        'e2e-cy-dp-failing.job.zip',
    );
});

Cypress.Commands.add('cleanTestJobs', () => {
    return cy
        .fixture('lib/explore/test-jobs.json')
        .then((testJobs) => {
            return Promise.all(
                testJobs.map((testJob) => {
                    const normalizedTestJob = applyGlobalEnvSettings(testJob);

                    return deleteTestJobIfExists(normalizedTestJob);
                }),
            );
        })
        .then(() => {
            return cy
                .fixture('lib/explore/additional-test-job.json')
                .then((testJob) => {
                    const normalizedTestJob = applyGlobalEnvSettings(testJob);

                    return deleteTestJobIfExists(normalizedTestJob);
                });
        });
});

Cypress.Commands.add('waitForTestJobExecutionCompletion', () => {
    const waitForJobExecutionTimeout = 180000; // Wait up to 3 min for job execution to complete

    return cy.fixture('lib/manage/e2e-cypress-dp-test.json').then((testJob) => {
        const normalizedTestJob = applyGlobalEnvSettings(testJob);

        return waitForJobExecutionCompletion(
            normalizedTestJob.team,
            normalizedTestJob.job_name,
            waitForJobExecutionTimeout,
        );
    });
});

Cypress.Commands.add('createTwoExecutionsLongLivedTestJob', () => {
    const waitForJobExecutionTimeout = 180000; // Wait up to 3 min for job execution to complete

    return cy.fixture('lib/manage/e2e-cypress-dp-test.json').then((testJob) => {
        const normalizedTestJob = applyGlobalEnvSettings(testJob);

        return createExecutionsForJob(
            normalizedTestJob.team,
            normalizedTestJob.job_name,
            waitForJobExecutionTimeout,
            2,
        );
    });
});

Cypress.Commands.add('createExecutionsLongLivedFailingTestJob', () => {
    const waitForJobExecutionTimeout = 180000; // Wait up to 3 min for job execution to complete

    return cy.fixture('e2e-cy-dp-failing.job.json').then((failingTestJob) => {
        const normalizedTestJob = applyGlobalEnvSettings(failingTestJob);

        return createExecutionsForJob(
            normalizedTestJob.team,
            normalizedTestJob.job_name,
            waitForJobExecutionTimeout,
            2,
        );
    });
});

Cypress.Commands.add(
    'changeDataJobEnabledStatus',
    (teamName, jobName, status) => {
        return cy
            .request({
                url:
                    Cypress.env('data_jobs_url') +
                    `/data-jobs/for-team/${teamName}/jobs/${jobName}/deployments`,
                method: 'get',
                auth: {
                    bearer: window.localStorage.getItem('access_token'),
                },
                failOnStatusCode: false,
            })
            .then((outerResponse) => {
                if (outerResponse.status === 200) {
                    const lastDeployment =
                        outerResponse.body[outerResponse.body.length - 1];
                    const lastDeploymentHash = lastDeployment.job_version;

                    return cy
                        .request({
                            url:
                                Cypress.env('data_jobs_url') +
                                `/data-jobs/for-team/${teamName}/jobs/${jobName}/deployments/${lastDeploymentHash}`,
                            method: 'patch',
                            body: { enabled: status },
                            auth: {
                                bearer: window.localStorage.getItem(
                                    'access_token',
                                ),
                            },
                            failOnStatusCode: false,
                        })
                        .then((innerResponse) => {
                            if (
                                innerResponse.status >= 200 &&
                                innerResponse.status < 300
                            ) {
                                cy.log(
                                    `Change enable status to [${status}] for data job [${jobName}]`,
                                );
                            } else {
                                cy.log(
                                    `Cannot change enabled status to [${status}] for data job [${jobName}]`,
                                );

                                console.log(`Http request:`, innerResponse);
                            }

                            return cy.wrap({
                                context:
                                    'commands::1::changeDataJobEnabledStatus()',
                                action: 'continue',
                            });
                        });
                } else {
                    cy.log(
                        `Cannot change enabled status to [${status}] for data job [${jobName}]`,
                    );

                    console.log(`Http request:`, outerResponse);

                    return cy.wrap({
                        context: 'commands::2::changeDataJobEnabledStatus()',
                        action: 'continue',
                    });
                }
            });
    },
);
