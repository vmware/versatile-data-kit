/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { HttpBackend, HttpClient } from '@angular/common/http';
import { AuthConfig } from 'angular-oauth2-oidc';
import { AppConfig, RefreshTokenConfig } from './app-config.model';
import { firstValueFrom } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class AppConfigService {
    private httpClient: HttpClient;
    private appConfig: AppConfig;

    constructor(private httpBackend: HttpBackend) {
        this.httpClient = new HttpClient(httpBackend);
    }

    loadAppConfig(): Promise<void> {
        return firstValueFrom(this.httpClient.get<AppConfig>('/assets/data/appConfig.json').pipe()).then((data) => {
            this.appConfig = data;
        });
    }

    getConfig(): AppConfig {
        return this.appConfig;
    }

    getSkipAuth(): boolean {
        return this.appConfig.auth.skipAuth;
    }

    getAuthCodeFlowConfig(): AuthConfig {
        if (this.getSkipAuth()) return new AuthConfig();
        const replaceWindowLocationOrigin = (str: string): string => {
            return str?.replace('$window.location.origin', window.location.origin);
        };

        const authCodeFlowConfig: AuthConfig = this.getConfig()?.auth.authConfig;
        authCodeFlowConfig.redirectUri = replaceWindowLocationOrigin(authCodeFlowConfig?.redirectUri);
        authCodeFlowConfig.silentRefreshRedirectUri = replaceWindowLocationOrigin(authCodeFlowConfig?.silentRefreshRedirectUri);
        return authCodeFlowConfig;
    }

    getRefreshTokenConfig(): RefreshTokenConfig {
        if (this.getSkipAuth()) return null;
        return this.getConfig()?.auth.refreshTokenConfig;
    }
}
