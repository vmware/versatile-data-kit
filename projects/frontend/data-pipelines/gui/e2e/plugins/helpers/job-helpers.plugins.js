/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

const fs = require("fs");
const path = require("path");

const { Logger } = require("./logger-helpers.plugins");

const { applyGlobalEnvSettings } = require("./util-helpers.plugins");

const {
    httpDeleteReq,
    httpGetReq,
    httpPostReq,
    httpPatchReq,
} = require("./http-helpers.plugins");

/**
 * ** Create and Deploy Data jobs if they don't exist.
 *
 * @param {{relativePathToFixtures: Array<{pathToFixture:string; pathToZipFile:string;}>}} taskConfig - configuration for task.
 *      relativePathToFixtures provides relative paths for fixtures files starting from directory fixtures
 *      e.g. {
 *             relativePathToFixtures: [
 *                  {
 *                      pathToFixture: '/base/data-jobs/cy-e2e-team-z-dp-lib-failing-v0.json',
 *                      pathToZipFile: '/base/data-jobs/cy-e2e-team-z-dp-lib-failing-v0.zip'
 *                  }
 *             ]
 *           }
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<boolean>}
 */
const createDeployJobs = (taskConfig, config) => {
    const startTime = new Date();

    Logger.info("Trying to load Data jobs fixtures and binaries.");
    Logger.debug(`Start time =>`, startTime.toISOString());

    return (
        _loadFixturesValuesAndBinariesPaths(taskConfig.relativePathToFixtures)
            .then((commands) => {
                return Promise.all(
                    // Send multiple parallel stream for Data jobs resolution
                    commands.map((command, index) => {
                        Logger.debug(`Data job fixture =>`, command.jobFixture);

                        return (
                            Promise
                                // Pass command down the stream
                                .resolve({ ...command, index })
                                // Send requests to get Data job
                                .then((prevCommand) => {
                                    return _getDataJobDeployments(
                                        prevCommand.jobFixture,
                                        config,
                                    ).then((response) => {
                                        return {
                                            ...prevCommand,
                                            response,
                                        };
                                    });
                                })
                                // Check what is the state of requested Job, if it's deployed, or exist but not deployed, or doesn't exist at all
                                .then((prevCommand) => {
                                    const jobFixture = prevCommand.jobFixture;
                                    const jobName = jobFixture.job_name;
                                    const httpResponse = prevCommand.response;

                                    let nextAction = "done";

                                    if (
                                        httpResponse.status === 200 &&
                                        httpResponse.data.length > 0
                                    ) {
                                        Logger.info(
                                            `Data job "${jobName}" is already existing, therefore skipping creation and deployment.`,
                                        );
                                    } else if (
                                        httpResponse.status === 200 &&
                                        httpResponse.data.length === 0
                                    ) {
                                        Logger.info(
                                            `Data job "${jobName}" exists, but it is not deployed. Will start deploying...`,
                                        );
                                        nextAction = "deploy";
                                    } else if (httpResponse.status === 404) {
                                        Logger.info(
                                            `Data job "${jobName}" not found. Will start creating...`,
                                        );
                                        nextAction = "create";
                                    }

                                    return {
                                        ...prevCommand,
                                        nextAction,
                                    };
                                })
                                // Send request to create Job if its doesn't exist, otherwise pass execution to the next step
                                .then((prevCommand) => {
                                    const currentAction =
                                        prevCommand.nextAction;
                                    const jobFixture = prevCommand.jobFixture;
                                    const jobName = jobFixture.job_name;

                                    if (currentAction === "create") {
                                        return _createDataJob(
                                            jobFixture,
                                            config,
                                        ).then((response) => {
                                            if (response.status === 201) {
                                                return {
                                                    ...prevCommand,
                                                    nextAction: "deploy",
                                                };
                                            } else {
                                                Logger.error(
                                                    `Failed to create Data job "${jobName}"`,
                                                );

                                                throw new Error(
                                                    `Failed to create Data job "${jobName}"`,
                                                );
                                            }
                                        });
                                    }

                                    return {
                                        ...prevCommand,
                                    };
                                })
                                // Send request to deploy Job if it was created on previous step
                                .then((prevCommandOuter) => {
                                    const currentAction =
                                        prevCommandOuter.nextAction;
                                    const jobFixture =
                                        prevCommandOuter.jobFixture;
                                    const pathToZipFile =
                                        prevCommandOuter.pathToZipFile;
                                    const jobName = jobFixture.job_name;

                                    if (currentAction === "deploy") {
                                        if (!pathToZipFile) {
                                            Logger.info(
                                                `Data job "${jobName}" doesn't have path to job zip file, therefore skipping deployment.`,
                                            );
                                        } else {
                                            Logger.debug(
                                                `Loading Job Zip binary located on =>`,
                                                pathToZipFile,
                                            );

                                            let jobZipFile;

                                            try {
                                                jobZipFile = fs.readFileSync(
                                                    pathToZipFile,
                                                    { encoding: "base64" },
                                                );
                                            } catch (error) {
                                                Logger.error(
                                                    `Cannot read file located on =>`,
                                                    pathToZipFile,
                                                );

                                                throw error;
                                            }

                                            return new Promise((resolve) => {
                                                setTimeout(
                                                    () =>
                                                        resolve(
                                                            prevCommandOuter,
                                                        ),
                                                    prevCommandOuter.index *
                                                        2000 +
                                                        250,
                                                );
                                            }).then((prevCommandInner) => {
                                                return _deployDataJob(
                                                    jobFixture,
                                                    jobZipFile,
                                                    config,
                                                ).then((result) => {
                                                    return {
                                                        ...prevCommandInner,
                                                        ...result,
                                                    };
                                                });
                                            });
                                        }
                                    }

                                    return {
                                        ...prevCommandOuter,
                                        code: 0,
                                    };
                                })
                                // Final step to validate if everything is OK
                                .then((prevCommand) => {
                                    if (prevCommand.code === 0) {
                                        return true;
                                    }

                                    const jobFixture = prevCommand.jobFixture;
                                    const jobName = jobFixture.job_name;

                                    Logger.error(
                                        `Failed to create/deploy Data job "${jobName}"`,
                                    );

                                    throw new Error(
                                        `Failed to create/deploy Data job "${jobName}".`,
                                    );
                                })
                        );
                    }),
                );
            })
            // Deployment to its end for all Jobs
            .finally(() => {
                const endTime = new Date();
                Logger.info(`Data jobs create/deployment to the end`);
                Logger.debug(
                    `End time => ${endTime.toISOString()};`,
                    `Elapsed => ${(endTime - startTime) / 1000}s`,
                );
            })
    );
};

/**
 * ** Trigger executions for Data jobs.
 *
 * @param {{relativePathToFixtures: Array<{pathToFixture:string;}>; executions?: number}} taskConfig - configuration for task.
 *      relativePathToFixtures provides relative paths for fixtures files starting from directory fixtures
 *      e.g. {
 *             relativePathToFixtures: [
 *                  {
 *                      pathToFixture: '/base/data-jobs/cy-e2e-team-z-dp-lib-failing-v0.json'
 *                  }
 *             ],
 *             executions: 2
 *           }
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<boolean>}
 */
const provideDataJobsExecutions = (taskConfig, config) => {
    const startTime = new Date();
    const targetExecutions = taskConfig.executions ?? 2;
    const jobExecutionTimeout = 180000; // Wait up to 3 min per Job for execution to complete

    Logger.info(
        `Trying to provide at least ${targetExecutions} executions for Data job fixtures`,
    );
    Logger.debug(`Start time =>`, startTime.toISOString());

    return (
        _loadFixturesValuesAndBinariesPaths(taskConfig.relativePathToFixtures)
            .then((commands) => {
                // Send requests to get data for all the Jobs
                return Promise.all(
                    commands.map((command, index) => {
                        Logger.debug(`Data job fixture =>`, command.jobFixture);

                        const jobFixture = command.jobFixture;
                        const jobName = jobFixture.job_name;

                        // Pass the command down the stream with timeouts to avoid glitch on the server
                        return (
                            new Promise((resolve) => {
                                setTimeout(
                                    () => resolve({ ...command }),
                                    index * 2150 + 350,
                                );
                            })
                                // Get Data job executions
                                .then((prevCommandOuter) => {
                                    return _getDataJobExecutionsArray(
                                        prevCommandOuter.jobFixture,
                                        config,
                                    ).then((executions) => {
                                        Logger.info(
                                            `For Data job "${jobName}" found ${executions.length} executions, while target is ${targetExecutions}`,
                                        );

                                        if (
                                            executions.length >=
                                            targetExecutions
                                        ) {
                                            Logger.info(
                                                `For Data job "${jobName}" skipping serial execution, because expected number found`,
                                            );

                                            if (
                                                executions.length >
                                                targetExecutions
                                            ) {
                                                return {
                                                    ...prevCommandOuter,
                                                    executions,
                                                    code: 0,
                                                };
                                            }

                                            // Wait to finish if there is already executing Data job and continue
                                            return waitForDataJobExecutionToComplete(
                                                jobFixture,
                                                jobExecutionTimeout,
                                                config,
                                            ).then(() => {
                                                return {
                                                    ...prevCommandOuter,
                                                    executions,
                                                    code: 0,
                                                };
                                            });
                                        }

                                        // Wait to finish if there is already executing Data job and continue
                                        return (
                                            waitForDataJobExecutionToComplete(
                                                jobFixture,
                                                jobExecutionTimeout,
                                                config,
                                            )
                                                .then(() => {
                                                    return {
                                                        ...prevCommandOuter,
                                                        executions,
                                                        code: 0,
                                                    };
                                                })
                                                // Get Data job last deployment
                                                .then((prevCommandInner) => {
                                                    return _getJobLastDeployment(
                                                        jobFixture,
                                                        config,
                                                    ).then((lastDeployment) => {
                                                        return {
                                                            ...prevCommandInner,
                                                            lastDeployment,
                                                            code: 0,
                                                        };
                                                    });
                                                })
                                                // If last deployment found trigger execution for Data job
                                                .then((prevCommandInner) => {
                                                    if (
                                                        prevCommandInner.lastDeployment
                                                    ) {
                                                        return _triggerExecutionForJob(
                                                            jobFixture,
                                                            jobExecutionTimeout,
                                                            prevCommandInner.lastDeployment,
                                                            targetExecutions -
                                                                prevCommandInner.executions,
                                                            config,
                                                        ).then((result) => {
                                                            return {
                                                                ...prevCommandInner,
                                                                ...result,
                                                            };
                                                        });
                                                    }

                                                    return {
                                                        ...prevCommandInner,
                                                        code: 1,
                                                    };
                                                })
                                        );
                                    });
                                })
                                // Final step to validate if everything is OK
                                .then((prevCommand) => {
                                    if (prevCommand.code === 0) {
                                        return true;
                                    }

                                    Logger.error(
                                        `Failed to provide at least ${targetExecutions} for Data job "${jobName}"`,
                                    );

                                    throw new Error(
                                        `Failed to provide at least ${targetExecutions} for Data job "${jobName}"`,
                                    );
                                })
                        );
                    }),
                );
            })
            // Executions to its end for all Jobs
            .finally(() => {
                const endTime = new Date();
                Logger.info(
                    `Provided at least ${targetExecutions} executions for Data job fixtures`,
                );
                Logger.debug(
                    `End time => ${endTime.toISOString()};`,
                    `Elapsed => ${(endTime - startTime) / 1000}s`,
                );
            })
    );
};

/**
 * ** Change Data Jobs statuses for provided fixtures.
 *
 * @param {{relativePathToFixtures: Array<{pathToFixture:string;}>; status: boolean;}} taskConfig - configuration for task.
 *      relativePathToFixtures provides relative paths for fixtures files starting from directory fixtures
 *      e.g. {
 *             relativePathToFixtures: [
 *                  {
 *                      pathToFixture: '/base/data-jobs/cy-e2e-team-z-dp-lib-failing-v0.json'
 *                  }
 *             ],
 *             status: boolean
 *           }
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<boolean>}
 */
const changeJobsStatusesFixtures = (taskConfig, config) => {
    const startTime = new Date();

    Logger.info(`Trying to disable Data Jobs for provided Data Jobs fixtures`);
    Logger.debug(`Start time =>`, startTime.toISOString());

    return (
        _loadFixturesValuesAndBinariesPaths(taskConfig.relativePathToFixtures)
            .then((commands) => {
                const jobFixtures = commands.map((command) =>
                    applyGlobalEnvSettings(command.jobFixture),
                );

                return Promise.all(
                    jobFixtures.map((jobFixture) => {
                        _getJobLastDeployment(jobFixture, config).then(
                            (lastDeployment) => {
                                if (
                                    !lastDeployment ||
                                    !lastDeployment.job_version
                                ) {
                                    Logger.info(
                                        `Deployment doesn't exist for Data Job ${jobFixture?.job_name}, skipping status change`,
                                    );

                                    return true;
                                }

                                const deploymentHash =
                                    lastDeployment.job_version;

                                return _updateDataJob(
                                    jobFixture.team,
                                    jobFixture.job_name,
                                    deploymentHash,
                                    { enabled: taskConfig.status },
                                    config,
                                ).then((updateResponse) => {
                                    if (
                                        updateResponse.status >= 200 &&
                                        updateResponse.status < 300
                                    ) {
                                        Logger.info(
                                            `Data Job ${jobFixture?.job_name} status changed to ${taskConfig.status}`,
                                        );
                                    } else {
                                        Logger.info(
                                            `Data Job ${jobFixture?.job_name} status cannot be changed`,
                                        );
                                    }

                                    return true;
                                });
                            },
                        );
                    }),
                );
            })
            .then((responses) => responses.every((value) => !!value))
            // Status change to its end for all Jobs
            .finally(() => {
                const endTime = new Date();
                Logger.debug(
                    `End time => ${endTime.toISOString()};`,
                    `Elapsed => ${(endTime - startTime) / 1000}s`,
                );
            })
    );
};

/**
 * ** Delete Jobs for provided fixtures paths.
 *
 * @param {{relativePathToFixtures: Array<{pathToFixture:string;}>}} taskConfig - configuration for task.
 *      relativePathToFixtures provides relative paths for fixtures files starting from directory fixtures
 *      e.g. {
 *             relativePathToFixtures: [
 *                  {
 *                      pathToFixture: '/base/data-jobs/cy-e2e-team-z-dp-lib-failing-v0.json'
 *                  }
 *             ]
 *           }
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<boolean>}
 */
const deleteJobsFixtures = (taskConfig, config) => {
    const startTime = new Date();

    Logger.info(`Trying to delete Data Jobs for provided Data Jobs fixtures`);
    Logger.debug(`Start time =>`, startTime.toISOString());

    return (
        _loadFixturesValuesAndBinariesPaths(taskConfig.relativePathToFixtures)
            .then((commands) => {
                const jobFixtures = commands.map(
                    (command) => command.jobFixture,
                );

                // Send requests to delete data for fixtures
                return deleteJobs(jobFixtures, config).then(() => {
                    Logger.info(
                        `Deleted Data Jobs: ${jobFixtures
                            .map((jobFixture) => jobFixture.job_name)
                            .toString()}`,
                    );

                    return true;
                });
            })
            // Executions to its end for all Jobs
            .finally(() => {
                const endTime = new Date();
                Logger.debug(
                    `End time => ${endTime.toISOString()};`,
                    `Elapsed => ${(endTime - startTime) / 1000}s`,
                );
            })
    );
};

/**
 * ** Delete jobs if they exist.
 *
 * @param {Array<{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}>} jobFixtures
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<boolean>}
 */
const deleteJobs = (jobFixtures, config) => {
    return Promise.all(
        jobFixtures.map((injectedJobFixture) => {
            const jobFixture = applyGlobalEnvSettings(injectedJobFixture);
            const jobName = jobFixture.job_name;

            Logger.info(`Trying to delete Data job "${jobName}"`);

            return _getDataJob(jobFixture, config).then((outerResponse) => {
                if (outerResponse.status === 200) {
                    return _deleteDataJob(jobFixture, config).then(() => {
                        Logger.info(`Data job "${jobName}" deleted`);

                        return true;
                    });
                }

                Logger.info(`Data job "${jobName}" doesn't exist`);

                return true;
            });
        }),
    ).then((responses) => responses.every((value) => !!value));
};

/**
 * ** Wait for Data job execution to complete.
 *
 * @param {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}} injectedJobFixture
 * @param {number} jobExecutionTimeout
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<{code: number}>}
 */
const waitForDataJobExecutionToComplete = (
    injectedJobFixture,
    jobExecutionTimeout,
    config,
) => {
    const jobFixture = applyGlobalEnvSettings(injectedJobFixture);
    const jobName = jobFixture.job_name;
    const pollInterval = 10000; // retry every 10s

    return _getDataJobExecutions(jobFixture, config).then((response) => {
        if (response.status !== 200) {
            Logger.info(`Failed Data job "${jobName}" executions polling`);

            return {
                code: 0,
            };
        }

        const lastFiveExecutions = response.data
            .sort(compareDatesASC)
            .slice(response.data.length > 5 ? response.data.length - 5 : 0);

        if (!lastFiveExecutions.length || lastFiveExecutions.length === 0) {
            Logger.info(`There is no Data job "${jobName}" execution to wait`);

            return {
                code: 0,
            };
        }

        const lastExecution = lastFiveExecutions[lastFiveExecutions.length - 1];
        const lastExecutionStatus = lastExecution.status.toLowerCase();

        if (
            lastExecutionStatus !== "running" &&
            lastExecutionStatus !== "submitted"
        ) {
            Logger.info(
                `Data job "${jobName}" executed successfully, polling completed`,
            );

            return {
                code: 0,
            };
        }

        if (jobExecutionTimeout <= 0) {
            Logger.info(
                `Data job "${jobName}" waiting time for execution exceeded, skipping and continue with next steps`,
            );

            return {
                code: 1,
            };
        }

        Logger.info(
            `Data job "${jobName}", still executing... retry after ${
                pollInterval / 1000
            } seconds`,
        );

        return new Promise((resolve) => {
            setTimeout(() => resolve(), pollInterval);
        }).then(() =>
            waitForDataJobExecutionToComplete(
                jobFixture,
                jobExecutionTimeout - pollInterval,
                config,
            ),
        );
    });
};

/**
 * ** Compare dates ASC.
 *
 * @param {number | any} left
 * @param {number | any} right
 * @returns {number}
 * @private
 */
const compareDatesASC = (left, right) => {
    const leftStartTime = left.start_time ? left.start_time : 0;
    const rightStartTime = right.start_time ? right.start_time : 0;

    return (
        new Date(leftStartTime).getTime() - new Date(rightStartTime).getTime()
    );
};

/**
 * ** Trigger Data job execution.
 *
 * @param {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}} jobFixture
 * @param {number} jobExecutionTimeout
 * @param lastDeployment
 * @param {number} neededExecutions
 * @param {Cypress.ResolvedConfigOptions} config
 * @param {number} counterOfExecutions
 * @returns {Promise<{code: number}>}
 * @private
 */
const _triggerExecutionForJob = (
    jobFixture,
    jobExecutionTimeout,
    lastDeployment,
    neededExecutions,
    config,
    counterOfExecutions = 0,
) => {
    const jobName = jobFixture.job_name;

    if (counterOfExecutions === 0) {
        Logger.info(
            `Submitting ${neededExecutions} serial executions for Data job "${jobName}"`,
        );
    } else {
        Logger.info(
            `Submitted ${counterOfExecutions} executions for Data job "${jobName}" and left ${
                neededExecutions - counterOfExecutions
            }`,
        );
    }

    if (neededExecutions === counterOfExecutions) {
        return Promise.resolve({ code: 0 });
    }

    // Trigger job execution
    return _executeJob(jobFixture, lastDeployment.id, config)
        .then((result) => {
            if (result.code === 0) {
                return new Promise((resolve) => {
                    setTimeout(() => resolve({ code: 0 }), 5000);
                });
            }

            return result;
        })
        .then(() =>
            waitForDataJobExecutionToComplete(
                jobFixture,
                jobExecutionTimeout,
                config,
            ),
        )
        .then(() =>
            _triggerExecutionForJob(
                jobFixture,
                jobExecutionTimeout,
                lastDeployment,
                neededExecutions,
                config,
                counterOfExecutions + 1,
            ),
        );
};

/**
 * ** Execute Data job.
 *
 * @param {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}} jobFixture
 * @param {string} deploymentId
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<{code: number}>}
 * @private
 */
const _executeJob = (jobFixture, deploymentId, config) => {
    const jobName = jobFixture.job_name;
    const teamName = jobFixture.team;
    const url = `${config.env["data_jobs_url"]}/data-jobs/for-team/${teamName}/jobs/${jobName}/deployments/${deploymentId}/executions`;

    Logger.info(`Submitting Data job execution for "${jobName}"`);

    return httpPostReq(url, {}).then((response) => {
        if (response.status >= 400) {
            Logger.info(`Failed to execute Data job "${jobName}"`);
        }

        return {
            code: 0,
        };
    });
};

/**
 * ** Get Data job executions always Array.
 *
 * @param {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}} jobFixture
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<Array<Record<any, any>>>}
 * @private
 */
const _getDataJobExecutionsArray = (jobFixture, config) => {
    const jobName = jobFixture.job_name;

    return _getDataJobExecutions(jobFixture, config).then((response) => {
        if (response.status !== 200) {
            Logger.info(`Failed to get Data job "${jobName}" executions`);

            return [];
        }

        return response.data && response.data.length ? response.data : [];
    });
};

/**
 * ** Get Data job last deployment.
 *
 * @param {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}} jobFixture
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<Record<any, any>>}
 * @private
 */
const _getJobLastDeployment = (jobFixture, config) => {
    const jobName = jobFixture.job_name;

    return _getDataJobDeployments(jobFixture, config).then((response) => {
        if (response.status !== 200) {
            Logger.info(`Failed to get Data job "${jobName}" deployments`);

            return null;
        }

        return response.data && response.data.length
            ? response.data[response.data.length - 1]
            : null;
    });
};

/**
 * ** Deploy data Job.
 *
 * @param {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}} jobFixture
 * @param {any} jobZipFile
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<{code: number}>}
 * @private
 */
const _deployDataJob = (jobFixture, jobZipFile, config) => {
    const jobName = jobFixture.job_name;
    const teamName = jobFixture.team;
    const waitForJobDeploymentTimeout = 300000; // Wait up to 5 min for deployment to complete.

    Logger.info(`Deploying Data job "${jobName}"`);

    // Upload Data Job resources
    return _sendDataJobResources(teamName, jobName, jobZipFile, config).then(
        (response1) => {
            if (response1.status > 400) {
                Logger.error(
                    `Failed to send Data job "${jobName}" resources to server`,
                );

                return {
                    code: 1,
                };
            }

            /**
             * @type {{version_sha: string}}
             */
            let jsonResponse;

            try {
                jsonResponse = response1.data;
            } catch (error) {
                Logger.error(
                    `Cannot parse response and read SHA for deployed Data jobs resources, response =>`,
                    response1,
                );

                throw error;
            }

            // Deploy data job
            return new Promise((resolve) => {
                setTimeout(() => resolve(), 1000);
            })
                .then(() =>
                    _deployDataJobSHAVersion(
                        teamName,
                        jobName,
                        jsonResponse.version_sha,
                        config,
                    ),
                )
                .then((response2) => {
                    if (response2.status === 202) {
                        Logger.info(
                            `Data job "${jobName}" deployment in progress...`,
                        );

                        return _waitForDataJobDeploymentToComplete(
                            jobFixture,
                            waitForJobDeploymentTimeout,
                            config,
                        );
                    }

                    return {
                        code: 0,
                    };
                });
        },
    );
};

/**
 * ** Wait for Data job deployment to finish.
 *
 * @param {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}} jobFixture
 * @param {number} timeout
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<{code: number}>}
 * @private
 */
const _waitForDataJobDeploymentToComplete = (jobFixture, timeout, config) => {
    const jobName = jobFixture.job_name;
    const waitInterval = 10000; // retry every 10s

    return _getDataJobDeployments(jobFixture, config).then((resp) => {
        if (resp.status === 200 && resp.data.length > 0) {
            Logger.info(`Data job "${jobName}" deployment finished`);

            return {
                code: 0,
            };
        }

        if (timeout <= 0) {
            Logger.info(
                `Data job "${jobName}" waiting time to deploy exceeded, skipping and continue with next steps`,
            );

            return {
                code: 0,
            };
        }

        Logger.info(
            `Data job "${jobName}", still deploying... retry after ${
                waitInterval / 1000
            } seconds`,
        );

        return new Promise((resolve) => {
            setTimeout(() => resolve(), waitInterval);
        }).then(() =>
            _waitForDataJobDeploymentToComplete(
                jobFixture,
                timeout - waitInterval,
                config,
            ),
        );
    });
};

/**
 * ** Create Data job.
 *
 * @param {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}} jobFixture
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<Record<any, any>>>}
 * @private
 */
const _createDataJob = (jobFixture, config) => {
    const teamName = jobFixture.team;
    const jobName = jobFixture.job_name;
    const url = `${config.env["data_jobs_url"]}/data-jobs/for-team/${teamName}/jobs`;

    Logger.debug(`Creating Data job "${jobName}" for Team "${teamName}"`);

    return httpPostReq(url, jobFixture);
};

/**
 * ** Update Data job.
 *
 * @param {string} teamName
 * @param {string} jobName
 * @param {string} deploymentHash
 * @param {{enabled:boolean;}} jobFixture
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<Record<any, any>>>}
 * @private
 */
const _updateDataJob = (
    teamName,
    jobName,
    deploymentHash,
    jobFixture,
    config,
) => {
    const url = `${config.env["data_jobs_url"]}/data-jobs/for-team/${teamName}/jobs/${jobName}/deployments/${deploymentHash}`;

    Logger.debug(`Updating Data job "${jobName}" for Team "${teamName}"`);

    return httpPatchReq(url, jobFixture);
};

/**
 * ** Get Data job.
 *
 * @param {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}} jobFixture
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<Record<any, any>>>}
 * @private
 */
const _getDataJob = (jobFixture, config) => {
    const teamName = jobFixture.team;
    const jobName = jobFixture.job_name;
    const url = `${config.env["data_jobs_url"]}/data-jobs/for-team/${teamName}/jobs/${jobName}`;

    Logger.debug(`Get Data job "${jobName}"`);

    return httpGetReq(url);
};

/**
 * ** Delete Data job.
 *
 * @param {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}} jobFixture
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<any>>}
 * @private
 */
const _deleteDataJob = (jobFixture, config) => {
    const teamName = jobFixture.team;
    const jobName = jobFixture.job_name;
    const url = `${config.env["data_jobs_url"]}/data-jobs/for-team/${teamName}/jobs/${jobName}`;

    Logger.debug(`Delete Data job "${jobName}"`);

    return httpDeleteReq(url);
};

/**
 * ** Get Data job executions.
 *
 * @param {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}} jobFixture
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<Array<Record<any, any>>>>}
 * @private
 */
const _getDataJobExecutions = (jobFixture, config) => {
    const jobName = jobFixture.job_name;
    const teamName = jobFixture.team;
    const url = `${config.env["data_jobs_url"]}/data-jobs/for-team/${teamName}/jobs/${jobName}/executions`;

    Logger.debug(`Get Data job "${jobName}" executions`);

    return httpGetReq(url);
};

/**
 * ** Get Data job deployments.
 *
 * @param {{job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}} jobFixture
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<Array<Record<any, any>>>>}
 * @private
 */
const _getDataJobDeployments = (jobFixture, config) => {
    const jobName = jobFixture.job_name;
    const teamName = jobFixture.team;
    const url = `${config.env["data_jobs_url"]}/data-jobs/for-team/${teamName}/jobs/${jobName}/deployments`;

    Logger.debug(`Get Data job "${jobName}" deployments`);

    return httpGetReq(url);
};

/**
 * ** Upload Data job resource file to deploy it.
 *
 * @param {string} teamName
 * @param {string} jobName
 * @param {any} jobZipFile
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<any>>}
 * @private
 */
const _sendDataJobResources = (teamName, jobName, jobZipFile, config) => {
    const url = `${config.env["data_jobs_url"]}/data-jobs/for-team/${teamName}/jobs/${jobName}/sources`;
    let buffer;

    try {
        buffer = Buffer.from(jobZipFile, "base64");
    } catch (error) {
        Logger.error(
            `Cannot convert from base64 to Buffer Data job "${jobName}" zip file`,
            error,
        );

        throw error;
    }

    Logger.debug(`Sending Data job resources to API, buffer =>`, buffer);

    return httpPostReq(url, buffer, { "Content-Type": "" });
};

/**
 * ** Deploy specific Data job deployment using SHA version.
 *
 * @param {string} teamName
 * @param {string} jobName
 * @param {string} shaVersion
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<any>>}
 * @private
 */
const _deployDataJobSHAVersion = (teamName, jobName, shaVersion, config) => {
    const url = `${config.env["data_jobs_url"]}/data-jobs/for-team/${teamName}/jobs/${jobName}/deployments`;

    Logger.debug(`Deploying Data job SHA version =>`, shaVersion);

    return httpPostReq(url, {
        job_version: shaVersion,
        mode: "release",
        enabled: true,
    });
};

/**
 * ** Load fixtures and binaries paths.
 *
 * @param {Array<{pathToFixture:string; pathToZipFile?:string;}>} pathToFixtures
 * @returns {Promise<Array<{config: Cypress.ResolvedConfigOptions, jobFixture: {job_name:string; description:string; team:string; config:{db_default_type:string; contacts:{}; schedule:{schedule_cron:string}; generate_keytab:boolean; enable_execution_notifications:boolean}}, pathToZipFile: string}>>}
 * @private
 */
const _loadFixturesValuesAndBinariesPaths = (pathToFixtures) => {
    return Promise.resolve(
        pathToFixtures.map((relativePathToFixture) => {
            return {
                pathToFixture: path.join(
                    __dirname,
                    `../../fixtures/${relativePathToFixture.pathToFixture.replace(
                        /^\//,
                        "",
                    )}`,
                ),
                pathToZipFile: relativePathToFixture.pathToZipFile
                    ? path.join(
                          __dirname,
                          `../../fixtures/${relativePathToFixture.pathToZipFile.replace(
                              /^\//,
                              "",
                          )}`,
                      )
                    : null,
            };
        }),
    ).then((pathToFixturesAndBinaries) => {
        // Resolving files and parsing to JSON and passing down the stream
        return pathToFixturesAndBinaries.map((data) => {
            const pathToFixture = data.pathToFixture;

            Logger.debug(
                `Loading Data job fixture located on =>`,
                pathToFixture,
            );

            let jobFile;
            let jobFixture;

            try {
                jobFile = fs.readFileSync(pathToFixture, { encoding: "utf8" });
            } catch (error) {
                Logger.error(`Cannot read file located on =>`, pathToFixture);

                throw error;
            }

            try {
                jobFixture = applyGlobalEnvSettings(JSON.parse(jobFile));

                return {
                    jobFixture,
                    pathToZipFile: data.pathToZipFile,
                };
            } catch (error) {
                Logger.error(
                    `Cannot parse read file located on =>`,
                    pathToFixture,
                );

                throw error;
            }
        });
    });
};

module.exports = {
    createDeployJobs,
    deleteJobsFixtures,
    deleteJobs,
    provideDataJobsExecutions,
    changeJobsStatusesFixtures,
    waitForDataJobExecutionToComplete,
    compareDatesASC,
};
