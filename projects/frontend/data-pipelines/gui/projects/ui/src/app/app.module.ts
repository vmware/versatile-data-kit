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

import { VmwComponentsModule } from '@vdk/shared';

import { TaurusSharedCoreModule, TaurusSharedFeaturesModule, TaurusSharedNgRxModule } from '@vdk/shared';

import { DataPipelinesModule } from '@vdk/data-pipelines';

import { AppComponent } from './app.component';
import { AppRouting } from './app.routing';
import { authCodeFlowConfig } from './auth';
import { AuthorizationInterceptor } from './http.interceptor';
import { GettingStartedComponent } from './getting-started/getting-started.component';

// eslint-disable-next-line prefer-arrow/prefer-arrow-functions
export function lottiePlayerLoader() {
    return import('lottie-web');
}

@NgModule({
    declarations: [AppComponent, GettingStartedComponent],
    imports: [
        AppRouting,
        BrowserModule,
        ClarityModule,
        BrowserAnimationsModule,
        ApolloModule,
        TaurusSharedCoreModule.forRoot(),
        TaurusSharedFeaturesModule.forRoot(),
        TaurusSharedNgRxModule.forRootWithDevtools(),
        TimeagoModule.forRoot(),
        LottieModule.forRoot({ player: lottiePlayerLoader }),
        VmwComponentsModule.forRoot(),
        DataPipelinesModule.forRoot({
            defaultOwnerTeamName: 'taurus',
            manageConfig: {
                allowKeyTabDownloads: true
            },
            exploreConfig: {
                showTeamsColumn: true
            },
            healthStatusUrl: '/explore/data-jobs?search={0}',
            showExecutionsPage: true,
            showLineagePage: false
        }),
        HttpClientModule,
        OAuthModule.forRoot({
            resourceServer: {
                allowedUrls: [
                    'https://console-stg.cloud.vmware.com/',
                    'https://gaz-preview.csp-vidm-prod.com/',
                    '/data-jobs'
                ],
                sendAccessToken: true
            }
        })
    ],
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
export class AppModule {
}
