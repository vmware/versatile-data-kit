/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright (c) 2022-2023. VMware
 * All rights reserved.
 */

const fs = require("fs");
const path = require("path");

const { Logger } = require("./logger-helpers.plugins");

const { USER_TEAMS_ROLE } = require("../../support/helpers/constants.support");

const { generateUUID } = require("./util-helpers.plugins");

const {
    httpGetReq,
    httpPatchReq,
    httpDeleteReq,
} = require("./http-helpers.plugins");

const { deleteMembers } = require("./members-helpers.plugins");

/**
 * ** Get Team.
 *
 * @param {string} teamName
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<{name: string; description: string; users: Array<{id: string; description: string}>; lakeNamespaces: Array<string>; collectors:Array<string>}>>}
 */
const getTeam = (teamName, config) => {
    const url = `${config.env["teams_url"]}/teams/${teamName}`;

    return httpGetReq(url);
};

/**
 * ** Create Update Team leveraging provided task config and config.
 *
 * @param {{fixture: {name: string; description: string; users: Array<{id: string; description: string}>; lakeNamespaces: Array<string>; collectors:Array<string>}; forceUpdateIfExist: boolean}} taskConfig
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<{fixture: {name: string; description: string; users: Array<{id: string; description: string}>; lakeNamespaces: Array<string>; collectors:Array<string>}}>}
 */
const createUpdateTeam = (taskConfig, config) => {
    const startTime = new Date();

    Logger.info(`Trying to create/update Team`);
    Logger.debug(`Start time =>`, startTime.toISOString());

    return (
        Promise.resolve({ ...taskConfig })
            // Fetch Team
            .then((prevCommand) => {
                return getTeam(prevCommand.fixture.name, config).then(
                    (response) => {
                        return {
                            ...prevCommand,
                            response,
                        };
                    },
                );
            })
            // Create/Update Team
            .then((prevCommand) => {
                const teamName = prevCommand.fixture.name;
                const httpResponse = prevCommand.response;

                if (httpResponse.status === 200 && httpResponse.data) {
                    if (!prevCommand.forceUpdateIfExist) {
                        Logger.info(
                            `Team "${teamName}" exist, therefore will skip it`,
                        );

                        return {
                            ...prevCommand,
                            fixture: httpResponse.data,
                            response: null,
                            code: 0,
                        };
                    }

                    Logger.info(
                        `Team "${teamName}" exist, therefore it will only update`,
                    );
                } else {
                    Logger.info(
                        `Team "${teamName}" doesn't exist, therefore trying to create`,
                    );
                }

                return (
                    _createUpdateTeam(prevCommand.fixture, config)
                        // validate if Team is created/updated
                        .then((response) => {
                            const isSuccessful =
                                response.status === 200 ||
                                response.status === 201;

                            if (isSuccessful) {
                                Logger.info(
                                    `Team "${prevCommand.fixture.name}" successfully created/updated`,
                                );
                            } else {
                                Logger.error(
                                    `Failed to create/update Team "${prevCommand.fixture.name}"`,
                                );

                                throw new Error(
                                    `Failed to create/update team "${prevCommand.fixture.name}".`,
                                );
                            }

                            return {
                                ...prevCommand,
                                fixture: response.data,
                                response: null,
                                code: 0,
                            };
                        })
                );
            })
            // Team create/update to its end
            .finally(() => {
                const endTime = new Date();
                Logger.info(`Team create/update to its end`);
                Logger.debug(
                    `End time => ${endTime.toISOString()};`,
                    `Elapsed => ${(endTime - startTime) / 1000}s`,
                );
            })
    );
};

/**
 * ** Creates Teams using e2e fixtures data, leveraging provided task config.
 *
 * @param {{relativePathToFixtures: string[], forceUpdateIfExist: boolean}} taskConfig
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<boolean>}
 */
const createTeams = (taskConfig, config) => {
    const startTime = new Date();

    Logger.info(`Trying to load Teams fixtures`);
    Logger.debug(`Start time =>`, startTime.toISOString());

    // Give fixtures paths down the stream
    return (
        Promise.resolve(
            taskConfig.relativePathToFixtures
                .map((relativePath) => relativePath.replace(/^\/+/, ""))
                .map((relativePathNormalized) =>
                    path.join(
                        __dirname,
                        `../../fixtures/${relativePathNormalized}`,
                    ),
                ),
        )
            .then((pathToFixtures) => {
                // Resolving files and parsing to JSON
                return Promise.all(
                    pathToFixtures.map((pathFixture, index) => {
                        return (
                            Promise.resolve({
                                ...taskConfig,
                                pathFixture,
                                index,
                            })
                                // Read file from system
                                .then((prevCommand) => {
                                    Logger.debug(
                                        `Loading Team fixture located on =>`,
                                        prevCommand.pathFixture,
                                    );

                                    let teamFile;
                                    /**
                                     * @type {{name: string; description: string; users: Array<{id: string; description: string}>; lakeNamespaces: Array<string>; collectors:Array<string>}}
                                     */
                                    let teamFixture;

                                    try {
                                        teamFile = fs.readFileSync(
                                            prevCommand.pathFixture,
                                            { encoding: "utf8" },
                                        );
                                    } catch (error) {
                                        Logger.error(
                                            `Cannot read file located on =>`,
                                            prevCommand.pathFixture,
                                        );

                                        throw error;
                                    }

                                    try {
                                        teamFixture = JSON.parse(teamFile);

                                        return {
                                            ...prevCommand,
                                            teamFixture,
                                        };
                                    } catch (error) {
                                        Logger.error(
                                            `Cannot parse read file located on =>`,
                                            prevCommand.pathFixture,
                                        );

                                        throw error;
                                    }
                                })
                                // Fetch Team
                                .then((prevCommand) => {
                                    const teamFixture = prevCommand.teamFixture;

                                    Logger.debug(
                                        `Team fixture =>`,
                                        prevCommand.teamFixture,
                                    );

                                    return getTeam(
                                        teamFixture.name,
                                        config,
                                    ).then((response) => {
                                        return {
                                            ...prevCommand,
                                            teamFixture,
                                            response,
                                        };
                                    });
                                })
                                // Check if Team exist and if not exist create it
                                .then((prevCommand) => {
                                    const teamFixture = prevCommand.teamFixture;
                                    const teamName = teamFixture.name;
                                    const httpResponse = prevCommand.response;

                                    if (
                                        httpResponse.status === 200 &&
                                        httpResponse.data
                                    ) {
                                        if (!prevCommand.forceUpdateIfExist) {
                                            Logger.info(
                                                `Team "${teamName}" exist, therefore will skip it`,
                                            );

                                            return {
                                                ...prevCommand,
                                                response: null,
                                                teamFixture: httpResponse.data,
                                                teamName,
                                                code: 0,
                                            };
                                        }

                                        Logger.info(
                                            `Team "${teamName}" exist, therefore it will only update`,
                                        );
                                    } else {
                                        Logger.info(
                                            `Team "${teamName}" doesn't exist, therefore trying to create`,
                                        );
                                    }

                                    return new Promise((resolve) => {
                                        setTimeout(
                                            () => resolve(prevCommand),
                                            prevCommand.index * 750 + 250,
                                        );
                                    }).then((command) => {
                                        return (
                                            _createUpdateTeam(
                                                teamFixture,
                                                config,
                                            )
                                                // Final step to validate if everything is OK
                                                .then((response) => {
                                                    const isSuccessful =
                                                        response.status ===
                                                            200 ||
                                                        response.status === 201;

                                                    if (isSuccessful) {
                                                        Logger.info(
                                                            `Team "${teamName}" successfully created/updated`,
                                                        );
                                                    } else {
                                                        Logger.error(
                                                            `Failed to create Team "${teamName}"`,
                                                        );

                                                        throw new Error(
                                                            `Failed to create team "${teamName}".`,
                                                        );
                                                    }

                                                    return {
                                                        ...command,
                                                        teamName,
                                                        response: null,
                                                        code: 0,
                                                    };
                                                })
                                        );
                                    });
                                })
                        );
                    }),
                );
            })
            // Teams creation to its end
            .finally(() => {
                const endTime = new Date();
                Logger.info(`Teams creation to its end`);
                Logger.debug(
                    `End time => ${endTime.toISOString()};`,
                    `Elapsed => ${(endTime - startTime) / 1000}s`,
                );
            })
    );
};

/**
 * ** Delete Team leveraging provided task config and config.
 *
 * @param {{teamFixture: {name: string; description: string; users: Array<{id: string; description: string}>; lakeNamespaces: Array<string>; collectors:Array<string>}; failOnError: boolean}} taskConfig
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<{teamFixture: {name: string; description: string; users: Array<{id: string; description: string}>; lakeNamespaces: Array<string>; collectors:Array<string>}}>}
 */
const deleteTeam = (taskConfig, config) => {
    const startTime = new Date();

    Logger.info(`Trying to delete Team`);
    Logger.debug(`Start time =>`, startTime.toISOString());

    const failOnError =
        typeof taskConfig.failOnError === "boolean"
            ? taskConfig.failOnError
            : true;

    return (
        Promise.resolve({ ...taskConfig })
            // Delete members from teamFixture and left only the first one
            .then((prevCommand) =>
                deleteMembers(
                    {
                        teamName: prevCommand.teamFixture.name,
                        members: prevCommand.teamFixture.users.splice(1),
                        failOnError,
                    },
                    config,
                ).then(() => {
                    return { ...prevCommand };
                }),
            )
            // Update Team to clean from related entities
            .then((prevCommand) => {
                const teamName = prevCommand.teamFixture.name;
                prevCommand.teamFixture.collectors.length = 0;
                prevCommand.teamFixture.lakeNamespaces.length = 0;

                Logger.debug(
                    `Updating Team "${teamName}" to clean from related entities`,
                );

                return (
                    _createUpdateTeam(prevCommand.teamFixture, config)
                        // Validate if team is updated
                        .then((response) => {
                            const isSuccessful =
                                response.status === 200 ||
                                response.status === 201;

                            if (isSuccessful) {
                                Logger.debug(
                                    `Team "${teamName}" successfully updated`,
                                );
                            } else {
                                Logger.error(
                                    `Failed to update Team "${teamName}"`,
                                );

                                if (failOnError) {
                                    throw new Error(
                                        `Failed to update team "${teamName}".`,
                                    );
                                }
                            }

                            return {
                                ...prevCommand,
                                teamName,
                                code: 0,
                            };
                        })
                );
            })
            .then((prevCommand) => {
                const teamName = prevCommand.teamFixture.name;

                return _deleteTeam(teamName, config).then((response) => {
                    if (response.status === 200) {
                        Logger.info(`Team "${teamName}" successfully deleted`);
                    } else {
                        Logger.error(`Failed to delete Team "${teamName}"`);

                        if (failOnError) {
                            throw new Error(
                                `Failed to delete team "${teamName}".`,
                            );
                        }
                    }

                    return {
                        ...prevCommand,
                        teamName,
                        code: 0,
                    };
                });
            })
            // Team delete to its end
            .finally(() => {
                const endTime = new Date();
                Logger.info(`Team delete to its end`);
                Logger.debug(
                    `End time => ${endTime.toISOString()};`,
                    `Elapsed => ${(endTime - startTime) / 1000}s`,
                );
            })
    );
};

/**
 * ** Generates random Teams leveraging provided task config and config.
 *
 * @param {{uuid: string; numberOfTeams: number}} taskConfig
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<Array<{ name: string; users: Array<{id: string; description: string}>; lakeNamespaces: Array<string>; collectors:Array<string>}>>}
 */
const generateRandomTeams = (taskConfig, config) => {
    const startTime = new Date();

    Logger.info(`Trying to generate random Teams`);
    Logger.debug(`Start time =>`, startTime.toISOString());

    const uuid = taskConfig.uuid ?? generateUUID();

    // Give fixtures paths down the stream
    return (
        Promise.resolve(
            path.join(
                __dirname,
                `../../fixtures/base/teams/team-template.json`,
            ),
        )
            .then((pathFixture) => {
                // Resolving file and parsing to JSON
                return (
                    Promise.resolve({ ...taskConfig, pathFixture, uuid })
                        // Read file from system
                        .then((prevCommand) => {
                            Logger.debug(
                                `Loading Team fixture located on =>`,
                                prevCommand.pathFixture,
                            );

                            let teamFile;
                            let teamFixture;

                            try {
                                teamFile = fs.readFileSync(
                                    prevCommand.pathFixture,
                                    { encoding: "utf8" },
                                );
                            } catch (error) {
                                Logger.error(
                                    `Cannot read file located on =>`,
                                    prevCommand.pathFixture,
                                );

                                throw error;
                            }

                            try {
                                teamFixture = JSON.parse(teamFile);

                                return {
                                    ...prevCommand,
                                    teamFixture,
                                };
                            } catch (error) {
                                Logger.error(
                                    `Cannot parse read file located on =>`,
                                    prevCommand.pathFixture,
                                );

                                throw error;
                            }
                        })
                        // Generate Teams
                        .then((prevCommand) => {
                            const teamFixture = { ...prevCommand.teamFixture };
                            const teams = [];

                            for (
                                let i = 0;
                                i < prevCommand.numberOfTeams;
                                i++
                            ) {
                                teams.push({
                                    ...teamFixture,
                                    name: `cy-e2e-team-v${i}-${uuid
                                        .replace(/-/g, "")
                                        .substring(16)}`,
                                    description:
                                        "One time used uuid Team, generated for the usage in e2e tests. Could be safely deleted when we do environment cleanup.",
                                    users: [
                                        {
                                            id: `cy-e2e-user-a${i}_${uuid
                                                .replace(/-/g, "")
                                                .substring(16)}@VMWARE.COM`,
                                            description:
                                                USER_TEAMS_ROLE.DATA_OWNER,
                                        },
                                        {
                                            id: `cy-e2e-user-b${i}_${uuid
                                                .replace(/-/g, "")
                                                .substring(16)}@VMWARE.COM`,
                                            description:
                                                USER_TEAMS_ROLE.TEAM_MEMBER,
                                        },
                                    ],
                                });
                            }

                            return teams;
                        })
                );
            })
            // Teams generate to its end
            .finally(() => {
                const endTime = new Date();
                Logger.info(`Teams generate to its end`);
                Logger.debug(
                    `End time => ${endTime.toISOString()};`,
                    `Elapsed => ${(endTime - startTime) / 1000}s`,
                );
            })
    );
};

/**
 * ** Create Update Team.
 *
 * @param {{name: string; description: string; users: Array<{id: string; description: string}>; lakeNamespaces: Array<string>; collectors:Array<string>}} teamFixture
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<{name: string; description: string; users: Array<{id: string; description: string}>; lakeNamespaces: Array<string>; collectors:Array<string>}>>}
 */
const _createUpdateTeam = (teamFixture, config) => {
    const teamName = teamFixture.name;
    const url = `${config.env["teams_url"]}/teams/${teamName}`;

    return new Promise((resolve) => {
        httpPatchReq(url, teamFixture).then((response) => {
            setTimeout(() => resolve(response), 1000);
        });
    });
};

/**
 * ** Delete Team.
 *
 * @param {string} teamName
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<any>>}
 * @private
 */
const _deleteTeam = (teamName, config) => {
    const url = `${config.env["teams_url"]}/teams/${teamName}`;

    return new Promise((resolve) => {
        httpDeleteReq(url).then((response) => {
            setTimeout(() => resolve(response), 1000);
        });
    });
};

module.exports = {
    getTeam,
    createUpdateTeam,
    createTeams,
    deleteTeam,
    generateRandomTeams,
};
