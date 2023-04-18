/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { AuthConfig } from 'angular-oauth2-oidc';

export interface AppConfig {
    refreshTokenStart?: number;
    orgLinkRoot?: string;
    consoleCloudUrl?: string;
    resourceServer?: ResourceServer;
    refreshTokenConfig?: RefreshTokenConfig;
    // $window.location.origin is replaced with the corresponding value dynamically upon loading,
    // see AppConfigService
    authConfig?: AuthConfig;
}

export interface ResourceServer {
    allowedUrls?: string[];
    sendAccessToken?: boolean;
}

export interface RefreshTokenConfig {
    refreshTokenRemainingTime?: number;
    refreshTokenCheckInterval?: number;
}
