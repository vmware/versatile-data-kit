/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

// Authentication

/**
 * ** CSP Id token key.
 * @type {string}
 */
const CSP_ID_TOKEN_KEY = 'id_token';

/**
 * ** CSP Access token key.
 * @type {string}
 */
const CSP_ACCESS_TOKEN_KEY = 'access_token';

/**
 * ** CSP Token expires at key.
 * @type {string}
 */
const CSP_EXPIRES_AT_KEY = 'expires_at';

/**
 * ** Long-lived Team that owns Data jobs for Data Pipelines feature.
 * @type {'cy-e2e-vdk'}
 */
const TEAM_VDK = 'cy-e2e-vdk';

/**
 * ** Long-lived Data job name owned from {@link: TEAM_VDK}
 * @type {'cy-e2e-vdk-failing-v0'}
 */
const TEAM_VDK_DATA_JOB_FAILING = 'cy-e2e-vdk-failing-v0';

/**
 * ** Short-lived Test Data job name v0 owned from {@link: TEAM_VDK} created in tests and deleted after suite.
 *
 *      - Have deployment.
 *
 * @type {'cy-e2e-vdk-test-v0'}
 */
const TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V0 = 'cy-e2e-vdk-test-v0';

/**
 * ** Short-lived Test Data job name v1 owned from {@link: TEAM_VDK} created in tests and deleted after suite.
 *
 *      - Have deployment.
 *
 * @type {'cy-e2e-vdk-test-v1'}
 */
const TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V1 = 'cy-e2e-vdk-test-v1';

/**
 * ** Short-lived Test Data job name v2 owned from {@link: TEAM_VDK} created in tests and deleted after suite.
 *
 *      - Have deployment.
 *
 * @type {'cy-e2e-vdk-test-v2'}
 */
const TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V2 = 'cy-e2e-vdk-test-v2';

/**
 * ** Short-lived Test Data job name v10 owned from {@link: TEAM_VDK} created in tests and deleted after suite.
 *
 *      - Doesn't have deployment.
 *
 * @type {'cy-e2e-vdk-test-v10'}
 */
const TEAM_VDK_DATA_JOB_TEST_V10 = 'cy-e2e-vdk-test-v10';

/**
 * ** Short-lived Test Data job name v11 owned from {@link: TEAM_VDK} created in tests and deleted after suite.
 *
 *      - Doesn't have deployment.
 *
 * @type {'cy-e2e-vdk-test-v11'}
 */
const TEAM_VDK_DATA_JOB_TEST_V11 = 'cy-e2e-vdk-test-v11';

/**
 * ** Short-lived Test Data job name v12 owned from {@link: TEAM_VDK} created in tests and deleted after suite.
 *
 *      - Doesn't have deployment.
 *
 * @type {'cy-e2e-vdk-test-v12'}
 */
const TEAM_VDK_DATA_JOB_TEST_V12 = 'cy-e2e-vdk-test-v12';

const BASIC_AUTH_CONFIG = {
    consoleCloudUrl: 'https://console-stg.cloud.vmware.com/',
    orgLinkRoot: '/csp/gateway/am/api/orgs/',
    authConfig: {
        issuer: 'https://console-stg.cloud.vmware.com/csp/gateway/am/api/',
        redirectUri: '$window.location.origin/',
        skipIssuerCheck: true,
        requestAccessToken: true,
        oidc: true,
        strictDiscoveryDocumentValidation: false,
        clientId: '8qQgcmhhsXuhGJs58ZW1hQ86h3eZXTpBV6t',
        responseType: 'code',
        scope: 'openid ALL_PERMISSIONS customer_number group_names',
        showDebugInformation: true,
        silentRefreshRedirectUri: '$window.location.origin/silent-refresh.html',
        useSilentRefresh: true,
        silentRefreshTimeout: 5000,
        timeoutFactor: 0.25,
        sessionChecksEnabled: true,
        clearHashAfterLogin: false,
        logoutUrl:
            'https://console-stg.cloud.vmware.com/csp/gateway/discovery?logout',
        nonceStateSeparator: 'semicolon'
    },
    resourceServer: {
        allowedUrls: [
            'https://console-stg.cloud.vmware.com/',
            'https://gaz-preview.csp-vidm-prod.com/',
            '/data-jobs'
        ],
        sendAccessToken: true
    },
    refreshTokenConfig: {
        start: 500,
        remainingTime: 360,
        checkInterval: 60
    }
};

module.exports = {
    BASIC_AUTH_CONFIG,
    CSP_ID_TOKEN_KEY,
    CSP_ACCESS_TOKEN_KEY,
    CSP_EXPIRES_AT_KEY,
    TEAM_VDK,
    TEAM_VDK_DATA_JOB_FAILING,
    TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V0,
    TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V1,
    TEAM_VDK_DATA_JOB_TEST_WITH_DEPLOY_V2,
    TEAM_VDK_DATA_JOB_TEST_V10,
    TEAM_VDK_DATA_JOB_TEST_V11,
    TEAM_VDK_DATA_JOB_TEST_V12
};
