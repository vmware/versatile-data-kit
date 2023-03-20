/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';

import { OAuthService } from 'angular-oauth2-oidc';

import { authCodeFlowConfig } from './auth';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent {
    constructor(private oauthService: OAuthService) {
        this.oauthService.configure(authCodeFlowConfig);
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        this.oauthService.loadDiscoveryDocumentAndLogin();
    }

    logout(): void {
        this.oauthService.logOut();
    }

    get idToken(): string {
        return this.oauthService.getIdToken();
    }

    get userName(): string {
        return this.oauthService.getIdentityClaims() ? this.getIdentityClaim('username') : 'N/A';
    }

    private getIdentityClaim(userNamePropName: string): string {
        return this.oauthService.getIdentityClaims()[userNamePropName] as string;
    }
}
