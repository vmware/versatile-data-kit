/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit, ViewContainerRef, Optional } from '@angular/core';

import { timer } from 'rxjs';

import { OAuthService } from 'angular-oauth2-oidc';

import { ConfirmationService, DynamicComponentsService, NavigationService, UrlOpenerService } from '@versatiledatakit/shared';

import { AppConfigService } from './app-config.service';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    title = 'core';
    collapsed = false;

    constructor(
        private readonly appConfigService: AppConfigService,
        @Optional() private readonly oauthService: OAuthService,
        private readonly navigationService: NavigationService,
        private readonly viewContainerRef: ViewContainerRef,
        private readonly dynamicComponentsService: DynamicComponentsService,
        private readonly confirmationService: ConfirmationService,
        private readonly urlOpenerService: UrlOpenerService
    ) {
        if (!this.skipAuth) {
            this.oauthService.configure(appConfigService.getAuthCodeFlowConfig());
            this.oauthService
                .loadDiscoveryDocumentAndLogin()
                .then(() => {
                    this.initTokenRefresh();
                })
                .catch(() => {
                    // No-op.
                });
        }
    }

    logout(): void {
        if (this.skipAuth) return;
        this.oauthService.logOut();
    }

    get skipAuth(): boolean {
        return this.appConfigService.getSkipAuth();
    }

    get idToken(): string {
        if (this.skipAuth) return null;
        return this.oauthService.getIdToken();
    }

    get userName(): string {
        if (this.skipAuth) return null;
        return this.oauthService.getIdentityClaims() ? this.getIdentityClaim('username') : 'N/A';
    }

    /**
     * @inheritDoc
     */
    ngOnInit(): void {
        this.navigationService.initialize();
        this.dynamicComponentsService.initialize(this.viewContainerRef);
        this.confirmationService.initialize();
        this.urlOpenerService.initialize();
    }

    private getIdentityClaim(userNamePropName: string): string {
        if (this.skipAuth) throw Error;
        const identityClaims = this.oauthService.getIdentityClaims() as {
            [key: string]: string;
        };

        return identityClaims[userNamePropName];
    }

    private initTokenRefresh() {
        if (this.skipAuth) throw Error;
        const refreshTokenConfig = this.appConfigService.getRefreshTokenConfig();
        timer(refreshTokenConfig.start, AppComponent.toMillis(refreshTokenConfig.checkInterval)).subscribe(() => {
            const remainiTimeMillis = this.oauthService.getAccessTokenExpiration() - Date.now();
            if (remainiTimeMillis <= AppComponent.toMillis(refreshTokenConfig.remainingTime)) {
                this.setCustomTokenAttributes(false, null);
                this.oauthService.refreshToken().finally(() => {
                    // No-op.
                });
            }
        });
    }

    private setCustomTokenAttributes(redirectToConsole: boolean, defaultOrg: { refLink: string }) {
        if (this.skipAuth) throw Error;
        const linkOrgQuery = this.getOrgLinkFromQueryParams(defaultOrg);
        const consoleCloudUrl = this.appConfigService.getConfig().auth.consoleCloudUrl;
        this.oauthService.customQueryParams = {
            orgLink: linkOrgQuery,
            targetUri: redirectToConsole ? consoleCloudUrl : window.location.href
        };
        if (redirectToConsole) {
            // Redirect to console cloud because we dont know the tenant url, but console does
            this.oauthService.redirectUri = consoleCloudUrl;
        }
    }

    private getOrgLinkFromQueryParams(defaultOrg: { refLink: string }): string {
        if (this.skipAuth) throw Error;
        const params = new URLSearchParams(window.location.search);
        const orgLinkUnderscored = params.get('org_link');
        const orgLinkBase = params.get('orgLink');
        if (orgLinkBase || orgLinkUnderscored) {
            return [orgLinkBase, orgLinkUnderscored].find((el) => el);
        } else {
            return defaultOrg ? defaultOrg.refLink : this.appConfigService.getConfig().auth.orgLinkRoot;
        }
    }

    private static toMillis(seconds: number) {
        return seconds * 1000;
    }
}
