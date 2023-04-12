/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { AuthConfig } from 'angular-oauth2-oidc';

export const authCodeFlowConfig: AuthConfig = {
    issuer: 'https://console-stg.cloud.vmware.com/csp/gateway/am/api/',
    redirectUri: window.location.origin + '/',
    skipIssuerCheck: true,
    requestAccessToken: true,
    oidc: true,
    strictDiscoveryDocumentValidation: false,
    clientId: '8qQgcmhhsXuhGJs58ZW1hQ86h3eZXTpBV6t',
    responseType: 'code',
    scope: 'openid ALL_PERMISSIONS customer_number group_names',
    showDebugInformation: true,
    silentRefreshRedirectUri: window.location.origin + '/silent-refresh.html',
    useSilentRefresh: true, // Needed for Code Flow to suggest using iframe-based refreshes
    silentRefreshTimeout: 5000, // For faster testing
    timeoutFactor: 0.25, // For faster testing
    sessionChecksEnabled: true,
    clearHashAfterLogin: false, // https://github.com/manfredsteyer/angular-oauth2-oidc/issues/457#issuecomment-431807040,
    logoutUrl: 'https://console-stg.cloud.vmware.com/csp/gateway/discovery?logout',
    nonceStateSeparator: 'semicolon' // Real semicolon gets mangled by IdentityServer's URI encoding
};

export const refreshTokenConfig = {
    // Remaining time (in seconds) during which, token refresh will be initalized. This value must be less than the token TTL
    refreshTokenRemainingTime: 360,

    // Check interval (in seconds), if token refresh need to be initalized. This value must be less than refreshTokenRemainingTime
    refreshTokenCheckInterval: 60
};
