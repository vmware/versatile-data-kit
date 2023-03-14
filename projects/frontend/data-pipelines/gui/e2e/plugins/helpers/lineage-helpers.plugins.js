/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright (c) 2023. VMware
 * All rights reserved.
 */

const { Logger } = require("./logger-helpers.plugins");

const { generateUUID } = require("./util-helpers.plugins");

const { httpGetReq, httpPutReq } = require("./http-helpers.plugins");

const {
    TEAM_NAME_DP_DATA_JOB_LINEAGE,
} = require("../../support/helpers/constants.support");

const TABLE_PREFIX = "lineage_table_";
const TABLE_1 = `${TABLE_PREFIX}1`;
const TABLE_2 = `${TABLE_PREFIX}2`;
const DATABASE_NAME = "history";

/**
 * ** Deploy Lineage Data to MMS if not exist.
 *
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<boolean>}
 */
const deployLineageData = (config) => {
    const startTime = new Date();

    Logger.info(`Trying to create Lineage Data to MMS if not exist`);
    Logger.debug(`Start time =>`, startTime.toISOString());

    return (
        Promise.resolve({})
            .then(() => {
                // Check if lineage exists and whether it has deployment or not.
                return _getLineageData(config).then((outerResponse) => {
                    if (outerResponse.status === 500) {
                        Logger.info(
                            `Failed to get Lineage Data from MMS for Data Job ${TEAM_NAME_DP_DATA_JOB_LINEAGE}, Internal Server Error - will create new one`,
                        );
                    } else if (
                        outerResponse.status === 200 &&
                        outerResponse.data.datasets.length > 0
                    ) {
                        Logger.info(
                            `Data Job ${TEAM_NAME_DP_DATA_JOB_LINEAGE} Lineage Data is already existing, therefore skipping creation`,
                        );

                        return true;
                    } else if (outerResponse.status === 404) {
                        Logger.info(
                            `Failed to get Lineage Data from MMS for Data Job ${TEAM_NAME_DP_DATA_JOB_LINEAGE}, Not Found - will create new one`,
                        );
                    } else if (
                        !outerResponse.data ||
                        !outerResponse.data.datasets ||
                        outerResponse.data.datasets.length === 0
                    ) {
                        Logger.info(
                            `Found Lineage Data from MMS for Data Job ${TEAM_NAME_DP_DATA_JOB_LINEAGE}, Datasets are missing - will create new one`,
                        );
                    } else {
                        return true;
                    }

                    const lineageData = {
                        type: "datajob_operation",
                        job_id: `datajob:${TEAM_NAME_DP_DATA_JOB_LINEAGE}`,
                        job_version: generateUUID().uuid.substring(0, 8),
                        input_datasets: [`${DATABASE_NAME}.${TABLE_1}`],
                        output_dataset: `${DATABASE_NAME}.${TABLE_2}`,
                        last_seen: Date.now(),
                    };

                    return _putLineageData(lineageData, config).then(
                        (innerResponse) => {
                            if (
                                innerResponse.status !== 200 &&
                                innerResponse.status !== 201
                            ) {
                                Logger.info(
                                    `Failed to create Lineage Data to MMS for Data Job ${TEAM_NAME_DP_DATA_JOB_LINEAGE}`,
                                );

                                return false;
                            }

                            Logger.info(
                                `Successfully create Lineage Data to MMS for Data Job ${TEAM_NAME_DP_DATA_JOB_LINEAGE}`,
                            );

                            return true;
                        },
                    );
                });
            })
            // Deploy lineage data to its end
            .finally(() => {
                const endTime = new Date();
                Logger.info(`Create Lineage Data to MMS to its end`);
                Logger.debug(
                    `End time => ${endTime.toISOString()};`,
                    `Elapsed => ${(endTime - startTime) / 1000}s`,
                );
            })
    );
};

/**
 * ** Get Lineage Data from MMS.
 *
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<any>>}
 * @private
 */
const _getLineageData = (config) => {
    const url = `${config.env["metadata_url"]}/metadata/lineage/datajob:${TEAM_NAME_DP_DATA_JOB_LINEAGE}?depth=1`;

    Logger.info(
        `Loading Lineage Data for Data Job: ${TEAM_NAME_DP_DATA_JOB_LINEAGE}`,
    );

    return new Promise((resolve) => {
        httpGetReq(url).then((response) => {
            setTimeout(() => resolve(response), 1000);
        });
    });
};

/**
 * ** Put Lineage Data to MMS.
 *
 * @param lineageData
 * @param {Cypress.ResolvedConfigOptions} config
 * @returns {Promise<AxiosResponse<any>>}
 * @private
 */
const _putLineageData = (lineageData, config) => {
    const url = `${config.env["metadata_url"]}/metadata/operations`;

    Logger.info(
        `Put Lineage Data for Data Job: ${TEAM_NAME_DP_DATA_JOB_LINEAGE}`,
    );
    Logger.debug(
        `For Data Job: ${TEAM_NAME_DP_DATA_JOB_LINEAGE}, trying to put Lineage Data: ${JSON.stringify(
            lineageData,
        )}`,
    );

    return new Promise((resolve) => {
        httpPutReq(url, lineageData).then((response) => {
            setTimeout(() => resolve(response), 1000);
        });
    });
};

module.exports = {
    deployLineageData,
    TABLE_PREFIX,
    TABLE_1,
    TABLE_2,
    DATABASE_NAME,
};
