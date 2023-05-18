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
