/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

const DEFAULT_TEST_ENV_VAR = "lib";

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

const createExecutionsForJob = (
    teamName,
    jobName,
    waitForJobExecutionTimeout,
    numberOfExecutions = 2,
) => {
    cy.log(
        `Trying to provide at least ${numberOfExecutions} executions for Job "${jobName}"`,
    );

    return _getJobExecutions(teamName, jobName).then((executions) => {
        cy.log(
            `Found ${executions.length} executions for Job "${jobName}" and target is ${numberOfExecutions} executions`,
        );

        if (executions.length >= numberOfExecutions) {
            cy.log(
                `Skipping manual execution, expected number of executions found`,
            );

            return cy.wrap({
                context: "commands.helpers::1::createExecutionsForJob()",
                action: "continue",
            });
        }

        return waitForJobExecutionCompletion(
            teamName,
            jobName,
            waitForJobExecutionTimeout,
        ).then(() => {
            return _getJobLastDeployment(teamName, jobName).then(
                (lastDeployment) => {
                    if (lastDeployment) {
                        return _executeCreateExecutionsForJob(
                            teamName,
                            jobName,
                            waitForJobExecutionTimeout,
                            lastDeployment,
                            executions,
                            numberOfExecutions,
                        );
                    }

                    return cy.wrap({
                        context:
                            "commands.helpers::2::createExecutionsForJob()",
                        action: "continue",
                    });
                },
            );
        });
    });
};

const waitForJobExecutionCompletion = (
    teamName,
    jobName,
    jobExecutionTimeout,
    loopStep = 0,
) => {
    const pollInterval = 5000;

    return cy
        .request({
            url:
                Cypress.env("data_jobs_url") +
                `/data-jobs/for-team/${teamName}/jobs/${jobName}/executions`,
            method: "get",
            auth: {
                bearer: window.localStorage.getItem("access_token"),
            },
        })
        .then((response) => {
            if (response.status !== 200) {
                cy.log(
                    `Job execution poll failed. Status: ${response.status}; Message: ${response.body}`,
                );

                return cy.wrap({
                    context:
                        "commands.helpers::1::waitForJobExecutionCompletion()",
                    action: "continue",
                });
            }

            const lastExecutions = response.body
                .sort((left, right) => _compareDatesAsc(left, right))
                .slice(response.body.length > 5 ? response.body.length - 5 : 0);

            if (!lastExecutions.length || lastExecutions.length === 0) {
                cy.log(`No valid Job executions available.`);

                return cy.wrap({
                    context:
                        "commands.helpers::2::waitForJobExecutionCompletion()",
                    action: "continue",
                });
            }

            const lastExecution = lastExecutions[lastExecutions.length - 1];
            const lastExecutionStatus = lastExecution.status.toLowerCase();

            if (
                lastExecutionStatus !== "running" &&
                lastExecutionStatus !== "submitted"
            ) {
                return (
                    loopStep > 0
                        ? cy.wait(pollInterval)
                        : cy.wrap({
                              context:
                                  "commands.helpers::3::waitForJobExecutionCompletion()",
                              action: "continue",
                          })
                ).then(() => {
                    cy.log(
                        `Job "${jobName}" executed successfully, polling completed!`,
                    );

                    return cy.wrap({
                        context:
                            "commands.helpers::4::waitForJobExecutionCompletion()",
                        action: "continue",
                    });
                });
            }

            if (jobExecutionTimeout <= 0) {
                cy.log(
                    "Time to wait exceeded! Will not wait for job execution to finish any longer.",
                );

                return cy.wrap({
                    context:
                        "commands.helpers::5::waitForJobExecutionCompletion()",
                    action: "continue",
                });
            }

            cy.log(
                `Job ${jobName}, still executing... Retrying after: ${
                    pollInterval / 1000
                } seconds`,
            );

            return cy
                .wait(pollInterval)
                .then(() =>
                    waitForJobExecutionCompletion(
                        teamName,
                        jobName,
                        jobExecutionTimeout - pollInterval,
                        jobExecutionTimeout++,
                    ),
                );
        });
};

const createTestJob = (testJob) => {
    let teamName = testJob.team;

    return cy
        .request({
            // TODO: use jobsQuery - deprecated jobsList in favour of jobsQuery
            url:
                Cypress.env("data_jobs_url") +
                `/data-jobs/for-team/${teamName}/jobs`,
            method: "post",
            body: testJob,
            auth: {
                bearer: window.localStorage.getItem("access_token"),
            },
            failOnStatusCode: false,
        })
        .then((response) => {
            if (response.status >= 400) {
                cy.log(
                    `Http request fail for url:`,
                    `/data-jobs/for-team/${teamName}/jobs`,
                );

                console.log(`Http request error:`, response);
            }

            return cy.wrap(response);
        });
};

const deleteTestJobIfExists = (testJob) => {
    let teamName = testJob.team;
    let jobName = testJob.job_name;

    return cy
        .request({
            url:
                Cypress.env("data_jobs_url") +
                `/data-jobs/for-team/${teamName}/jobs/${jobName}`,
            method: "get",
            auth: {
                bearer: window.localStorage.getItem("access_token"),
            },
            failOnStatusCode: false,
        })
        .then((outerResponse) => {
            if (outerResponse.status === 200) {
                return cy
                    .request({
                        url:
                            Cypress.env("data_jobs_url") +
                            `/data-jobs/for-team/${teamName}/jobs/${jobName}`,
                        method: "delete",
                        auth: {
                            bearer: window.localStorage.getItem("access_token"),
                        },
                        failOnStatusCode: false,
                    })
                    .then((innerResponse) => {
                        if (innerResponse.status >= 400) {
                            cy.log(
                                `Http request fail for url:`,
                                `/data-jobs/for-team/${teamName}/jobs/${jobName}`,
                            );

                            console.log(`Http request error:`, innerResponse);
                        }

                        return cy.wrap({
                            context:
                                "commands.helpers::1::deleteTestJobIfExists()",
                            action: "continue",
                        });
                    });
            } else if (outerResponse.status >= 400) {
                cy.log(
                    `Http request fail for url:`,
                    `/data-jobs/for-team/${teamName}/jobs/${jobName}`,
                );

                console.log(`Http request error:`, outerResponse);
            }

            return cy.wrap({
                context: "commands.helpers::2::deleteTestJobIfExists()",
                action: "continue",
            });
        });
};

const deployTestJobIfNotExists = (pathToJobData, pathToJobBinary) => {
    return cy.fixture(pathToJobData).then((testJob) => {
        const normalizedTestJob = applyGlobalEnvSettings(testJob);
        const teamName = normalizedTestJob.team;
        const jobName = normalizedTestJob.job_name;

        // Check if data job exists and wether it has deployment or not.
        return cy
            .request({
                url:
                    Cypress.env("data_jobs_url") +
                    `/data-jobs/for-team/${teamName}/jobs/${jobName}/deployments`,
                method: "get",
                auth: {
                    bearer: window.localStorage.getItem("access_token"),
                },
                failOnStatusCode: false,
            })
            .then((outerResponse) => {
                if (
                    outerResponse.status === 200 &&
                    outerResponse.body.length > 0
                ) {
                    cy.log(
                        jobName +
                            " is already existing, therefore skipping creation and deployment.",
                    );
                } else if (
                    outerResponse.status === 200 &&
                    outerResponse.body.length === 0
                ) {
                    cy.log(
                        jobName +
                            " exists, but it is not deployed. Deploying...",
                    );

                    return _deployTestDataJob(
                        normalizedTestJob,
                        pathToJobBinary,
                    );
                } else if (outerResponse.status === 404) {
                    return createTestJob(normalizedTestJob).then(
                        (innerResponse) => {
                            if (innerResponse.status === 201) {
                                return _deployTestDataJob(
                                    normalizedTestJob,
                                    pathToJobBinary,
                                );
                            } else {
                                throw new Error(
                                    "Failed to create job: " + jobName,
                                );
                            }
                        },
                    );
                } else if (outerResponse.status >= 400) {
                    cy.log(
                        `Http request fail for url:`,
                        `/data-jobs/for-team/${teamName}/jobs/${jobName}/deployments`,
                    );

                    console.log(`Http request error:`, outerResponse);
                }

                return cy.wrap({
                    context: "commands.helpers::deployTestJobIfNotExists()",
                    action: "continue",
                });
            });
    });
};

function _loadTestEnvironmentVar() {
    let testEnv = Cypress?.env("test_environment");

    if (!testEnv) {
        console.log(
            `DataPipelines test_environment is not set. Using default: ${DEFAULT_TEST_ENV_VAR}`,
        );
        testEnv = DEFAULT_TEST_ENV_VAR;
    }

    return testEnv;
}

function _executeCreateExecutionsForJob(
    teamName,
    jobName,
    waitForJobExecutionTimeout,
    lastDeployment,
    executions,
    numberOfExecutions,
    counterOfExecutions = 0,
) {
    const neededExecutions = numberOfExecutions - executions.length;

    if (counterOfExecutions === 0) {
        cy.log(`Submitting ${neededExecutions} serial executions`);
    } else {
        cy.log(
            `${
                neededExecutions - counterOfExecutions
            } more executions left for executing`,
        );
    }

    if (neededExecutions === counterOfExecutions) {
        return cy.wrap({
            context: "commands.helpers::1::_executeCreateExecutionsForJob()",
            action: "continue",
        });
    }

    return _executeJob(teamName, jobName, lastDeployment.id)
        .then(() => {
            return cy.wait(5000).then(() =>
                cy.wrap({
                    context:
                        "commands.helpers::2::_executeCreateExecutionsForJob()",
                    action: "continue",
                }),
            );
        })
        .then(() => {
            return waitForJobExecutionCompletion(
                teamName,
                jobName,
                waitForJobExecutionTimeout,
            );
        })
        .then(() => {
            return _executeCreateExecutionsForJob(
                teamName,
                jobName,
                waitForJobExecutionTimeout,
                lastDeployment,
                executions,
                numberOfExecutions,
                counterOfExecutions + 1,
            );
        });
}

function _getJobExecutions(teamName, jobName) {
    cy.log(`Fetching Job executions for Job "${jobName}"`);

    return cy
        .request({
            url: `/data-jobs/for-team/${teamName}/jobs/${jobName}/executions`,
            method: "get",
            auth: {
                bearer: window.localStorage.getItem("access_token"),
            },
        })
        .then((response) => {
            if (response.status !== 200) {
                cy.log(
                    `Getting Job executions failed. Status: ${response.status}; Message: ${response.body}`,
                );

                return cy.wrap([]);
            }

            return cy.wrap(
                response.body && response.body.length ? response.body : [],
            );
        });
}

function _getJobLastDeployment(teamName, jobName) {
    cy.log(`Fetching Job deployments for Job "${jobName}"`);

    return cy
        .request({
            url:
                Cypress.env("data_jobs_url") +
                `/data-jobs/for-team/${teamName}/jobs/${jobName}/deployments`,
            method: "get",
            auth: {
                bearer: window.localStorage.getItem("access_token"),
            },
        })
        .then((response) => {
            if (response.status !== 200) {
                cy.log(
                    `Getting Job deployments failed. Status: ${response.status}; Message: ${response.body}`,
                );

                return cy.wrap(null);
            }

            return cy.wrap(
                response.body && response.body.length
                    ? response.body[response.body.length - 1]
                    : null,
            );
        });
}

function _executeJob(teamName, jobName, deploymentId) {
    cy.log(`Submitting execution for Job "${jobName}"`);

    return cy
        .request({
            url:
                Cypress.env("data_jobs_url") +
                `/data-jobs/for-team/${teamName}/jobs/${jobName}/deployments/${deploymentId}/executions`,
            method: "post",
            auth: {
                bearer: window.localStorage.getItem("access_token"),
            },
            body: {},
        })
        .then((response) => {
            if (response.status >= 400) {
                cy.log(
                    `Executing Job failed. Status: ${response.status}; Message: ${response.body}`,
                );
            }

            return cy.wrap({
                context: "commands.helpers::_executeJob()",
                action: "continue",
            });
        });
}

function _compareDatesAsc(left, right) {
    const leftStartTime = left.start_time ? left.start_time : 0;
    const rightStartTime = right.start_time ? right.start_time : 0;

    return (
        new Date(leftStartTime).getTime() - new Date(rightStartTime).getTime()
    );
}

function _deployTestDataJob(testJob, pathToJobBinary) {
    const teamName = testJob.team;
    const jobName = testJob.job_name;
    const waitForJobDeploymentTimeout = 300000; // Wait up to 5 min for deployment to complete.

    cy.log(`Deploying Job ${jobName}`);

    // Upload Data Job code
    return cy.fixture(pathToJobBinary, "binary").then((zippedDataJob) => {
        return cy
            .request({
                url:
                    Cypress.env("data_jobs_url") +
                    "/data-jobs/for-team/" +
                    teamName +
                    "/jobs/" +
                    jobName +
                    "/sources",
                method: "post",
                auth: {
                    bearer: window.localStorage.getItem("access_token"),
                },
                body: Cypress.Blob.binaryStringToBlob(zippedDataJob),
            })
            .then((response1) => {
                let jsonResponse = JSON.parse(
                    Cypress.Blob.arrayBufferToBinaryString(response1.body),
                );

                // Deploy data job
                return cy
                    .request({
                        url:
                            Cypress.env("data_jobs_url") +
                            "/data-jobs/for-team/" +
                            teamName +
                            "/jobs/" +
                            jobName +
                            "/deployments",
                        method: "post",
                        auth: {
                            bearer: window.localStorage.getItem("access_token"),
                        },
                        body: {
                            job_version: jsonResponse.version_sha,
                            mode: "release",
                            enabled: true,
                        },
                    })
                    .then((response2) => {
                        if (response2.status === 202) {
                            cy.log(
                                `Job: ${jobName} deployment in progress. Waiting for deployment to complete`,
                            );

                            return _waitForDeploymentToFinish(
                                testJob,
                                waitForJobDeploymentTimeout,
                            );
                        }

                        return cy.wrap({
                            context: "commands.helpers::_deployTestDataJob()",
                            action: "continue",
                        });
                    });
            });
    });
}

function _waitForDeploymentToFinish(testJob, timeout) {
    const teamName = testJob.team;
    const jobName = testJob.job_name;
    const waitInterval = 5000;

    return cy
        .request({
            url:
                Cypress.env("data_jobs_url") +
                "/data-jobs/for-team/" +
                teamName +
                "/jobs/" +
                jobName +
                "/deployments",
            method: "get",
            auth: {
                bearer: window.localStorage.getItem("access_token"),
            },
        })
        .then((resp) => {
            if (resp.status === 200 && resp.body.length > 0) {
                cy.log("Job deployment finished!");

                return cy.wrap({
                    context:
                        "commands.helpers::1::_waitForDeploymentToFinish()",
                    action: "continue",
                });
            }

            if (timeout <= 0) {
                cy.log(
                    "Time to wait exceeded! Will not wait for job deployment to finish any longer.",
                );

                return cy.wrap({
                    context:
                        "commands.helpers::2::_waitForDeploymentToFinish()",
                    action: "continue",
                });
            }

            cy.log(
                `Job ${jobName}, still not deployed.. retrying after: ${
                    waitInterval / 1000
                } seconds`,
            );

            return cy
                .wait(waitInterval)
                .then(() =>
                    _waitForDeploymentToFinish(testJob, timeout - waitInterval),
                );
        });
}

module.exports = {
    applyGlobalEnvSettings,
    createExecutionsForJob,
    waitForJobExecutionCompletion,
    createTestJob,
    deleteTestJobIfExists,
    deployTestJobIfNotExists,
};
