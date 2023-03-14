/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright (c) 2022-2023. VMware
 * All rights reserved.
 */

const { Logger } = require("./logger-helpers.plugins");

const { httpDeleteReq } = require("./http-helpers.plugins");

/**
 * ** Delete Members.
 *
 * @param {{teamName: string; members: Array<{id: string; description: string}>; failOnError: boolean}} taskConfig
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<{teamName: string; members: Array<{id: string; description: string}>; code: number}>}
 */
const deleteMembers = (taskConfig, config) => {
    const startTime = new Date();

    Logger.info(`Trying to delete Members`);
    Logger.debug(`Start time =>`, startTime.toISOString());

    const failOnError =
        typeof taskConfig.failOnError === "boolean"
            ? taskConfig.failOnError
            : true;

    return (
        Promise.resolve({ ...taskConfig })
            .then((prevCommand) => {
                const teamName = prevCommand.teamName;
                const members = prevCommand.members;

                return Promise.all(
                    members.map((member) => {
                        Logger.debug(`Trying to delete Member "${member.id}"`);

                        return (
                            _deleteMember(teamName, member.id, config)
                                // validate if Member is deleted
                                .then((response) => {
                                    if (response.status === 204) {
                                        Logger.info(
                                            `Member "${member.id}" is successfully deleted`,
                                        );
                                    } else {
                                        Logger.error(
                                            `Failed to delete Member "${member.id}"`,
                                        );

                                        if (failOnError) {
                                            throw new Error(
                                                `Failed to delete Member "${member.id}".`,
                                            );
                                        }
                                    }

                                    return {
                                        ...prevCommand,
                                        code: 0,
                                    };
                                })
                        );
                    }),
                ).then(() => {
                    return {
                        ...prevCommand,
                        code: 0,
                    };
                });
            })
            // Members delete to its end
            .finally(() => {
                const endTime = new Date();
                Logger.info(`Members delete to its end`);
                Logger.debug(
                    `End time => ${endTime.toISOString()};`,
                    `Elapsed => ${(endTime - startTime) / 1000}s`,
                );
            })
    );
};

/**
 * ** Delete Member.
 *
 * @param {string} teamName
 * @param {string} memberUsername
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<any>>}
 * @private
 */
const _deleteMember = (teamName, memberUsername, config) => {
    const url = `${config.env["teams_url"]}/teams/${teamName}/members/${memberUsername}`;

    return new Promise((resolve) => {
        httpDeleteReq(url).then((response) => {
            setTimeout(() => resolve(response), 1000);
        });
    });
};

module.exports = {
    deleteMembers,
};
