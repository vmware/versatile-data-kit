/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule } from '@angular/core';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { AuthConfig, OAuthModule, OAuthStorage } from 'angular-oauth2-oidc';

import { TimeagoModule } from 'ngx-timeago';
import { LottieModule } from 'ngx-lottie';

import { ApolloModule } from 'apollo-angular';

import { ClarityModule } from '@clr/angular';

import {
    VdkSharedCoreModule,
    VdkSharedFeaturesModule,
    VdkSharedNgRxModule,
    VdkSharedComponentsModule,
} from '@versatiledatakit/shared';

import { VdkDataPipelinesModule } from '@versatiledatakit/data-pipelines';

import { authCodeFlowConfig } from './auth';

import { AuthorizationInterceptor } from './http.interceptor';

import { AppRouting } from './app.routing';

import { AppComponent } from './app.component';

import { GettingStartedComponent } from './getting-started/getting-started.component';

// eslint-disable-next-line prefer-arrow/prefer-arrow-functions
export function lottiePlayerLoader() {
    return import('lottie-web');
}

@NgModule({
    imports: [
        AppRouting,
        BrowserModule,
        ClarityModule,
        BrowserAnimationsModule,
        HttpClientModule,
        OAuthModule.forRoot({
            resourceServer: {
                allowedUrls: [
                    'https://console-stg.cloud.vmware.com/',
                    'https://gaz-preview.csp-vidm-prod.com/',
                    '/data-jobs',
                ],
                sendAccessToken: true,
            },
        }),
        ApolloModule,
        TimeagoModule.forRoot(),
        LottieModule.forRoot({ player: lottiePlayerLoader }),
        VdkSharedCoreModule.forRoot(),
        VdkSharedFeaturesModule.forRoot(),
        VdkSharedNgRxModule.forRootWithDevtools(),
        VdkSharedComponentsModule.forRoot(),
        VdkDataPipelinesModule.forRoot({
            defaultOwnerTeamName: 'taurus',
            manageConfig: {
                allowKeyTabDownloads: true,
            },
            exploreConfig: {
                showTeamsColumn: true,
            },
            healthStatusUrl: '/explore/data-jobs?search={0}',
            showExecutionsPage: true,
            showLineagePage: false,
            dataPipelinesDocumentationUrl: '#',
        }),
    ],
    declarations: [AppComponent, GettingStartedComponent],
    providers: [
        {
            provide: OAuthStorage,
            useValue: localStorage,
        },
        {
            provide: AuthConfig,
            useValue: authCodeFlowConfig,
        },
        {
            provide: HTTP_INTERCEPTORS,
            useClass: AuthorizationInterceptor,
            multi: true,
        },
    ],
    bootstrap: [AppComponent],
})
export class AppModule {}
