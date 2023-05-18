/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { AuthConfig, OAuthResourceServerConfig } from 'angular-oauth2-oidc';

export interface AppConfig {
    auth: Auth;
    ignoreRoutes?: string[];
    ignoreComponents?: string[];
}

export interface Auth {
    skipAuth?: false;

    // Used for producing the AuthConfig.customQueryParams mapping for `orgLink` and `targetUri`
    consoleCloudUrl?: string;
    orgLinkRoot?: string;
    // $window.location.origin is replaced with the corresponding value dynamically upon loading,
    // see AppConfigService
    authConfig?: AuthConfig;
    resourceServer?: OAuthResourceServerConfig;
    // Used for token auto-refresh capability, in case a token is about to expire.
    refreshTokenConfig?: RefreshTokenConfig;
}

export interface RefreshTokenConfig {
    start?: number;
    remainingTime?: number;
    checkInterval?: number;
}

export const defaultAppConfig: AppConfig = {
    auth: {
        skipAuth: false,
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
            logoutUrl: 'https://console-stg.cloud.vmware.com/csp/gateway/discovery?logout',
            nonceStateSeparator: 'semicolon'
        },
        resourceServer: {
            allowedUrls: ['https://console-stg.cloud.vmware.com/', 'https://gaz-preview.csp-vidm-prod.com/', '/data-jobs'],
            sendAccessToken: true
        },
        refreshTokenConfig: {
            start: 500,
            remainingTime: 360,
            checkInterval: 60
        }
    },
    ignoreComponents: [],
    ignoreRoutes: []
};
