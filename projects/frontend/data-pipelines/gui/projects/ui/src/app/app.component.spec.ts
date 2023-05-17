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

import { AppConfigService } from './app-config.service';

import { AppComponent } from './app.component';
import { HttpBackend } from '@angular/common/http';

describe('AppComponent', () => {
    let routerServiceStub: jasmine.SpyObj<RouterService>;
    let navigationServiceStub: jasmine.SpyObj<NavigationService>;
    let viewContainerRefStub: jasmine.SpyObj<ViewContainerRef>;
    let dynamicComponentsServiceStub: jasmine.SpyObj<DynamicComponentsService>;
    let confirmationServiceStub: jasmine.SpyObj<ConfirmationService>;
    let urlOpenerServiceStub: jasmine.SpyObj<UrlOpenerService>;
    let appConfigServiceStub: jasmine.SpyObj<AppConfigService>;
    const configureTestingModule = (providersAdditional: any[]) => {
        const providersBase = [
            UrlHelperService,
            { provide: NavigationService, useValue: navigationServiceStub },
            { provide: RouterService, useValue: routerServiceStub },
            { provide: ViewContainerRef, useValue: viewContainerRefStub },
            { provide: DynamicComponentsService, useValue: dynamicComponentsServiceStub },
            { provide: ConfirmationService, useValue: confirmationServiceStub },
            { provide: UrlOpenerService, useValue: urlOpenerServiceStub },
            { provide: AppConfigService, useValue: appConfigServiceStub }
        ];
        TestBed.configureTestingModule({
            schemas: [NO_ERRORS_SCHEMA],
            declarations: [AppComponent],
            imports: [],
            providers: providersBase.concat(providersAdditional)
        });
    };

    beforeEach(() => {
        routerServiceStub = jasmine.createSpyObj<RouterService>('routerService', ['getState']);
        navigationServiceStub = jasmine.createSpyObj<NavigationService>('navigationService', ['initialize']);
        appConfigServiceStub = jasmine.createSpyObj<AppConfigService>('appConfigService', [
            'getConfig',
            'getAuthCodeFlowConfig',
            'getSkipAuth'
        ]);
        viewContainerRefStub = jasmine.createSpyObj<ViewContainerRef>('viewContainerRefStub', ['createComponent']);
        dynamicComponentsServiceStub = jasmine.createSpyObj<DynamicComponentsService>('dynamicComponentsServiceStub', ['initialize']);
        confirmationServiceStub = jasmine.createSpyObj<ConfirmationService>('confirmationServiceStub', ['initialize']);
        urlOpenerServiceStub = jasmine.createSpyObj<UrlOpenerService>('urlOpenerServiceStub', ['initialize']);
        routerServiceStub.getState.and.returnValue(new Subject());
    });

    it('should create the app with auth enabled', () => {
        appConfigServiceStub.getSkipAuth.and.returnValue(false);
        const oAuthServiceStub = jasmine.createSpyObj<OAuthService>('oAuthService', [
            'configure',
            'loadDiscoveryDocumentAndLogin',
            'getAccessTokenExpiration',
            'refreshToken',
            'logOut',
            'getIdToken',
            'getIdentityClaims'
        ]);
        oAuthServiceStub.getIdentityClaims.and.returnValue({});
        oAuthServiceStub.loadDiscoveryDocumentAndLogin.and.returnValue(Promise.resolve(true));
        oAuthServiceStub.getAccessTokenExpiration.and.returnValue(0);
        oAuthServiceStub.refreshToken.and.returnValue(Promise.resolve({} as TokenResponse));
        configureTestingModule([{ provide: OAuthService, useValue: oAuthServiceStub }]);

        const fixture = TestBed.createComponent(AppComponent);
        const app = fixture.componentInstance;
        expect(app).toBeTruthy();
    });

    it('should create the app with auth skipped', () => {
        appConfigServiceStub.getSkipAuth.and.returnValue(true);
        configureTestingModule([]);
        const fixture = TestBed.createComponent(AppComponent);
        const app = fixture.componentInstance;
        expect(app).toBeTruthy();
    });

    it('should create the app with no components ignored', () => {
        appConfigServiceStub.getConfig.and.returnValue({
            auth: {},
            ignoreComponents: [],
            ignoreRoutes: []
        });

        // skip auth for convenience
        appConfigServiceStub.getSkipAuth.and.returnValue(true);

        configureTestingModule([]);
        const fixture = TestBed.createComponent(AppComponent);
        const app = fixture.componentInstance;
        expect(app).toBeTruthy();
        expect(app.explorePageVisible).toBeTrue();
    });

    it('should create the app with explore page ignored', () => {
        appConfigServiceStub.getConfig.and.returnValue({
            auth: {},
            ignoreComponents: ['explorePage'],
            ignoreRoutes: []
        });

        // skip auth for convenience
        appConfigServiceStub.getSkipAuth.and.returnValue(true);

        configureTestingModule([]);
        const fixture = TestBed.createComponent(AppComponent);
        const app = fixture.componentInstance;
        expect(app).toBeTruthy();
        expect(app.explorePageVisible).toBeFalse();
    });
});
