/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA, ViewContainerRef } from '@angular/core';

import { Subject } from 'rxjs';

import { OAuthService, UrlHelperService } from 'angular-oauth2-oidc';
import { TokenResponse } from 'angular-oauth2-oidc/types';

import {
    ConfirmationService,
    DynamicComponentsService,
    NavigationService,
    RouterService,
    UrlOpenerService
} from '@versatiledatakit/shared';

import { AppConfig } from './app-config.model';

import { AppConfigService } from './app-config.service';

import { AppComponent } from './app.component';

describe('AppComponent', () => {
    let routerServiceStub: jasmine.SpyObj<RouterService>;
    let oAuthServiceStub: jasmine.SpyObj<OAuthService>;
    let navigationServiceStub: jasmine.SpyObj<NavigationService>;
    let viewContainerRefStub: jasmine.SpyObj<ViewContainerRef>;
    let dynamicComponentsServiceStub: jasmine.SpyObj<DynamicComponentsService>;
    let confirmationServiceStub: jasmine.SpyObj<ConfirmationService>;
    let urlOpenerServiceStub: jasmine.SpyObj<UrlOpenerService>;
    let appConfigServiceStub: jasmine.SpyObj<AppConfigService>;

    beforeEach(() => {
        routerServiceStub = jasmine.createSpyObj<RouterService>('routerService', ['getState']);
        oAuthServiceStub = jasmine.createSpyObj<OAuthService>('oAuthService', [
            'configure',
            'loadDiscoveryDocumentAndLogin',
            'getAccessTokenExpiration',
            'refreshToken',
            'logOut',
            'getIdToken',
            'getIdentityClaims'
        ]);
        navigationServiceStub = jasmine.createSpyObj<NavigationService>('navigationService', ['initialize']);
        viewContainerRefStub = jasmine.createSpyObj<ViewContainerRef>('viewContainerRefStub', ['createComponent']);
        dynamicComponentsServiceStub = jasmine.createSpyObj<DynamicComponentsService>('dynamicComponentsServiceStub', ['initialize']);
        confirmationServiceStub = jasmine.createSpyObj<ConfirmationService>('confirmationServiceStub', ['initialize']);
        urlOpenerServiceStub = jasmine.createSpyObj<UrlOpenerService>('urlOpenerServiceStub', ['initialize']);
        appConfigServiceStub = jasmine.createSpyObj<AppConfigService>('appConfigService', ['getConfig', 'getAuthCodeFlowConfig']);

        routerServiceStub.getState.and.returnValue(new Subject());
        oAuthServiceStub.getIdentityClaims.and.returnValue({});
        oAuthServiceStub.loadDiscoveryDocumentAndLogin.and.returnValue(Promise.resolve(true));
        oAuthServiceStub.getAccessTokenExpiration.and.returnValue(0);
        oAuthServiceStub.refreshToken.and.returnValue(Promise.resolve({} as TokenResponse));
        appConfigServiceStub.getConfig.and.returnValue({} as AppConfig);

        TestBed.configureTestingModule({
            schemas: [NO_ERRORS_SCHEMA],
            declarations: [AppComponent],
            imports: [],
            providers: [
                UrlHelperService,
                { provide: OAuthService, useValue: oAuthServiceStub },
                { provide: NavigationService, useValue: navigationServiceStub },
                { provide: RouterService, useValue: routerServiceStub },
                { provide: ViewContainerRef, useValue: viewContainerRefStub },
                { provide: DynamicComponentsService, useValue: dynamicComponentsServiceStub },
                { provide: ConfirmationService, useValue: confirmationServiceStub },
                { provide: UrlOpenerService, useValue: urlOpenerServiceStub },
                { provide: AppConfigService, useValue: appConfigServiceStub }
            ]
        });
    });

    it('should create the app', () => {
        const fixture = TestBed.createComponent(AppComponent);
        const app = fixture.componentInstance;
        expect(app).toBeTruthy();
    });
});
