/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule } from '@angular/core';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { AuthConfig, OAuthModule, OAuthStorage } from 'angular-oauth2-oidc';

import { ClarityModule } from '@clr/angular';

import { VdkSharedCoreModule, VdkSharedFeaturesModule, VdkSharedNgRxModule, VdkSharedComponentsModule } from '@versatiledatakit/shared';

import { AuthorizationInterceptor } from './http.interceptor';

import { authCodeFlowConfig } from './auth';

import { AppRoutingModule } from './app-routing.module';

import { AppComponent } from './app.component';

@NgModule({
    imports: [
        AppRoutingModule,
        BrowserModule,
        ClarityModule,
        BrowserAnimationsModule,
        VdkSharedComponentsModule.forRoot(),
        VdkSharedCoreModule.forRoot(),
        VdkSharedFeaturesModule.forRoot({
            warning: {
                serviceRequestUrl: '#'
            },
            placeholder: {
                serviceRequestUrl: '#'
            }
        }),
        VdkSharedNgRxModule.forRootWithDevtools(),
        HttpClientModule,
        OAuthModule.forRoot({
            resourceServer: {
                allowedUrls: [authCodeFlowConfig.issuer, '/metadata'],
                sendAccessToken: true
            }
        })
    ],
    declarations: [AppComponent],
    providers: [
        {
            provide: OAuthStorage,
            useValue: localStorage
        },
        {
            provide: AuthConfig,
            useValue: authCodeFlowConfig
        },
        {
            provide: HTTP_INTERCEPTORS,
            useClass: AuthorizationInterceptor,
            multi: true
        }
    ],
    bootstrap: [AppComponent]
})
export class AppModule {}
