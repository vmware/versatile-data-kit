/*
 * Copyright 2023-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

// Users related

/**
 * ** Predefined User roles as Member in Team.
 *
 * @type {{DATA_OWNER: string, TECHNICAL_DATA_STEWARD: string, TEAM_MEMBER: string}}
 */
const USER_TEAMS_ROLE = {
    DATA_OWNER: "Data Owner",
    TECHNICAL_DATA_STEWARD: "Technical Data Steward",
    TEAM_MEMBER: "Team Member",
};

// General Assets by feature

/**
 * ** Long-lived Team that owns Data jobs from Data Pipelines library.
 * @type {'cy-e2e-team-z-dp-lib'}
 */
const TEAM_NAME_DP = "cy-e2e-team-z-dp-lib";

/**
 * ** Long-lived Data job name owned from {@link: TEAM_NAME_DP}
 * @type {'cy-e2e-team-z-dp-lib-failing-v0'}
 */
const TEAM_NAME_DP_DATA_JOB_FAILING = "cy-e2e-team-z-dp-lib-failing-v0";

/**
 * ** Long-lived Data job name owned from {@link: TEAM_NAME_DP} that has lineage for it.
 * @type {'cy-e2e-team-z-dp-lib-lineage-v1'}
 */
const TEAM_NAME_DP_DATA_JOB_LINEAGE = "cy-e2e-team-z-dp-lib-lineage-v1";

/**
 * ** Long-lived Data job name owned from {@link: TEAM_NAME_DP} that has lineage for it.
 * @type {'cy-e2e-team-z-dp-lib-test-v0'}
 */
const TEAM_NAME_DP_DATA_JOB_TEST = "cy-e2e-team-z-dp-lib-test-v0";

/**
 * ** Short-lived Test Data job name v1 owned from {@link: TEAM_NAME_DP} created in tests and deleted after suite.
 * @type {'cy-e2e-team-z-dp-lib-test-v1'}
 */
const TEAM_NAME_DP_DATA_JOB_TEST_V1 = "cy-e2e-team-z-dp-lib-test-v1";

/**
 * ** Short-lived Test Data job name v2 owned from {@link: TEAM_NAME_DP} created in tests and deleted after suite.
 * @type {'cy-e2e-team-z-dp-lib-test-v2'}
 */
const TEAM_NAME_DP_DATA_JOB_TEST_V2 = "cy-e2e-team-z-dp-lib-test-v2";

/**
 * ** Short-lived Test Data job name v3 owned from {@link: TEAM_NAME_DP} created in tests and deleted after suite.
 * @type {'cy-e2e-team-z-dp-lib-test-v3'}
 */
const TEAM_NAME_DP_DATA_JOB_TEST_V3 = "cy-e2e-team-z-dp-lib-test-v3";

module.exports = {
    USER_TEAMS_ROLE,
    TEAM_NAME_DP,
    TEAM_NAME_DP_DATA_JOB_FAILING,
    TEAM_NAME_DP_DATA_JOB_LINEAGE,
    TEAM_NAME_DP_DATA_JOB_TEST,
    TEAM_NAME_DP_DATA_JOB_TEST_V1,
    TEAM_NAME_DP_DATA_JOB_TEST_V2,
    TEAM_NAME_DP_DATA_JOB_TEST_V3,
};
