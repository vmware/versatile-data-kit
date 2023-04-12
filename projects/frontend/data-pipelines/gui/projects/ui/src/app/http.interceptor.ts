/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable, Optional } from '@angular/core';
import { OAuthModuleConfig, OAuthResourceServerErrorHandler, OAuthStorage } from 'angular-oauth2-oidc';
import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';

import { Observable } from 'rxjs';
import { authCodeFlowConfig } from './auth';

@Injectable()
export class AuthorizationInterceptor implements HttpInterceptor {
    constructor(
        private authStorage: OAuthStorage,
        private errorHandler: OAuthResourceServerErrorHandler,
        @Optional() private moduleConfig: OAuthModuleConfig
    ) {}

    /**
     * @inheritDoc
     */
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        const url = req.url.toLowerCase();
        if (!this.moduleConfig) {
            return next.handle(req);
        }

        if (!this.moduleConfig.resourceServer) {
            return next.handle(req);
        }

        if (!this.moduleConfig.resourceServer.allowedUrls) {
            return next.handle(req);
        }

        if (!this.checkUrl(url)) {
            return next.handle(req);
        }

        const sendAccessToken = this.moduleConfig.resourceServer.sendAccessToken;

        if (sendAccessToken && url.startsWith(authCodeFlowConfig.issuer) && url.endsWith('api/auth/token')) {
            const headers = req.headers.set('Authorization', 'Basic ' + btoa(authCodeFlowConfig.clientId + ':'));

            return next.handle(req.clone({ headers }));
        } else if (sendAccessToken) {
            const token = this.authStorage.getItem('access_token');
            const header = `Bearer ${token}`;
            const headers = req.headers.set('Authorization', header);

            return next.handle(req.clone({ headers }));
        }

        return next.handle(req);
    }

    private checkUrl(url: string): boolean {
        const found = this.moduleConfig.resourceServer.allowedUrls.find((u) => url.startsWith(u));
        return !!found;
    }
}
