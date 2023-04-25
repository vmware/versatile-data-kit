/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { HttpBackend, HttpClient } from '@angular/common/http';
import { AuthConfig } from 'angular-oauth2-oidc';
import { AppConfig, RefreshTokenConfig } from './app-config.model';
import { firstValueFrom } from 'rxjs';
import { Router } from '@angular/router';
import { routes } from './app.routing';
@Injectable({
    providedIn: 'root'
})
export class AppConfigService {
    private httpClient: HttpClient;
    private appConfig: AppConfig;
    private router: Router;

    constructor(private httpBackend: HttpBackend, private angularRouter: Router) {
        this.httpClient = new HttpClient(httpBackend);
        this.router = angularRouter;
    }

    async loadAppConfig(): Promise<void> {
        const data = await firstValueFrom(this.httpClient.get<AppConfig>('/assets/data/appConfig.json').pipe());
        this.appConfig = data;
        const localRoutes = routes.filter((route: { path: string }) => {
            return !data.ignoreRoutes.includes(route.path);
        });
        this.router.resetConfig(localRoutes);
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
