/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';

import { Subject } from 'rxjs';

import { OAuthService, UrlHelperService } from 'angular-oauth2-oidc';

import { NavigationService, RouterService } from '@vdk/shared';

import { AppComponent } from './app.component';
import { TokenResponse } from 'angular-oauth2-oidc/types';

describe('AppComponent', () => {
    let routerServiceStub: jasmine.SpyObj<RouterService>;
    let oAuthServiceStub: jasmine.SpyObj<OAuthService>;
    let navigationServiceStub: jasmine.SpyObj<NavigationService>;

    beforeEach(() => {
        routerServiceStub = jasmine.createSpyObj<RouterService>(
            'routerService',
            ['getState']
        );
        oAuthServiceStub = jasmine.createSpyObj<OAuthService>('oAuthService', [
            'configure',
            'loadDiscoveryDocumentAndLogin',
            'getAccessTokenExpiration',
            'refreshToken',
            'logOut',
            'getIdToken',
            'getIdentityClaims',
        ]);
        navigationServiceStub = jasmine.createSpyObj<NavigationService>(
            'navigationService',
            ['initialize']
        );

        routerServiceStub.getState.and.returnValue(new Subject());
        oAuthServiceStub.getIdentityClaims.and.returnValue({});
        oAuthServiceStub.loadDiscoveryDocumentAndLogin.and.returnValue(
            Promise.resolve(true)
        );
        oAuthServiceStub.getAccessTokenExpiration.and.returnValue(0);
        oAuthServiceStub.refreshToken.and.returnValue(
            Promise.resolve({} as TokenResponse)
        );

        TestBed.configureTestingModule({
            schemas: [NO_ERRORS_SCHEMA],
            declarations: [AppComponent],
            imports: [],
            providers: [
                UrlHelperService,
                { provide: OAuthService, useValue: oAuthServiceStub },
                { provide: NavigationService, useValue: navigationServiceStub },
                { provide: RouterService, useValue: routerServiceStub },
            ],
        });
    });

    it('should create the app', () => {
        const fixture = TestBed.createComponent(AppComponent);
        const app = fixture.componentInstance;
        expect(app).toBeTruthy();
    });
});
