/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';

import { timer } from 'rxjs';

import { OAuthService } from 'angular-oauth2-oidc';

import { NavigationService } from '@versatiledatakit/shared';

import { authCodeFlowConfig, refreshTokenConfig } from './auth';

const REFRESH_TOKEN_START = 500;
const ORG_LINK_ROOT = '/csp/gateway/am/api/orgs/';
const CONSOLE_CLOUD_URL = 'https://console-stg.cloud.vmware.com/';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss'],
})
export class AppComponent implements OnInit {
    title = 'core';
    collapsed = false;

    constructor(
        private readonly oauthService: OAuthService,
        private readonly navigationService: NavigationService
    ) {
        this.oauthService.configure(authCodeFlowConfig);
        this.oauthService
            .loadDiscoveryDocumentAndLogin()
            .then(() => {
                this.initTokenRefresh();
            })
            .catch(() => {
                // No-op.
            });
    }

    logout(): void {
        this.oauthService.logOut();
    }

    get idToken(): string {
        return this.oauthService.getIdToken();
    }

    get userName(): string {
        return this.oauthService.getIdentityClaims()
            ? this.getIdentityClaim('username')
            : 'N/A';
    }

    /**
     * @inheritDoc
     */
    ngOnInit(): void {
        this.navigationService.initialize();
    }

    private getIdentityClaim(userNamePropName: string): string {
        const identityClaims = this.oauthService.getIdentityClaims() as {
            [key: string]: string;
        };

        return identityClaims[userNamePropName];
    }

    private initTokenRefresh() {
        timer(
            REFRESH_TOKEN_START,
            AppComponent.toMillis(refreshTokenConfig.refreshTokenCheckInterval)
        ).subscribe(() => {
            const remainiTimeMillis =
                this.oauthService.getAccessTokenExpiration() - Date.now();
            if (
                remainiTimeMillis <=
                AppComponent.toMillis(
                    refreshTokenConfig.refreshTokenRemainingTime
                )
            ) {
                this.setCustomTokenAttributes(false, null);
                this.oauthService.refreshToken().finally(() => {
                    // No-op.
                });
            }
        });
    }

    private setCustomTokenAttributes(
        redirectToConsole: boolean,
        defaultOrg: { refLink: string }
    ) {
        const linkOrgQuery = AppComponent.getOrgLinkFromQueryParams(defaultOrg);
        this.oauthService.customQueryParams = {
            orgLink: linkOrgQuery,
            targetUri: redirectToConsole
                ? CONSOLE_CLOUD_URL
                : window.location.href,
        };
        if (redirectToConsole) {
            // Redirect to console cloud because we dont know the tenant url, but console does
            this.oauthService.redirectUri = CONSOLE_CLOUD_URL;
        }
    }

    private static getOrgLinkFromQueryParams(defaultOrg: {
        refLink: string;
    }): string {
        const params = new URLSearchParams(window.location.search);
        const orgLinkUnderscored = params.get('org_link');
        const orgLinkBase = params.get('orgLink');
        if (orgLinkBase || orgLinkUnderscored) {
            return [orgLinkBase, orgLinkUnderscored].find((el) => el);
        } else {
            return defaultOrg ? defaultOrg.refLink : ORG_LINK_ROOT;
        }
    }

    private static toMillis(seconds: number) {
        return seconds * 1000;
    }
}
