/*
 * Copyright 2021-2024 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgModule, APP_INITIALIZER } from '@angular/core';
import { HTTP_INTERCEPTORS, HttpBackend, HttpClientModule } from '@angular/common/http';
import { AppConfigService } from './app-config.service';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { AuthConfig, OAuthModule, OAuthModuleConfig, OAuthStorage } from 'angular-oauth2-oidc';

import { TimeagoModule } from 'ngx-timeago';
import { LottieModule } from 'ngx-lottie';

import { ApolloModule } from 'apollo-angular';

import { ClarityModule } from '@clr/angular';

import { VdkSharedCoreModule, VdkSharedFeaturesModule, VdkSharedNgRxModule, VdkSharedComponentsModule } from '@versatiledatakit/shared';

import { VdkDataPipelinesModule } from '@versatiledatakit/data-pipelines';

import { AuthorizationInterceptor } from './http.interceptor';

import { AppRouting } from './app.routing';

import { AppComponent } from './app.component';

import { GettingStartedComponent } from './getting-started/getting-started.component';
import { Router } from '@angular/router';

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
        OAuthModule.forRoot(),
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
                showTeamSectionInJobDetails: true
            },
            exploreConfig: {
                showTeamsColumn: true,
                showTeamSectionInJobDetails: true
            },
            healthStatusUrl: '/explore/data-jobs?search={0}',
            showExecutionsPage: true,
            showLineagePage: false,
            dataPipelinesDocumentationUrl: '#'
        })
    ],
    declarations: [AppComponent, GettingStartedComponent],
    providers: [
        { provide: AppConfigService, useClass: AppConfigService, deps: [HttpBackend, Router] },
        {
            deps: [AppConfigService],
            multi: true,
            provide: APP_INITIALIZER,
            useFactory: (appConfig: AppConfigService) => () => appConfig.loadAppConfig()
        },
        {
            provide: OAuthStorage,
            useValue: localStorage
        },
        {
            deps: [AppConfigService],
            provide: AuthConfig,
            useFactory: (appConfig: AppConfigService) => () => appConfig.getAuthCodeFlowConfig()
        },
        {
            deps: [AppConfigService],
            provide: OAuthModuleConfig,
            useFactory: (appConfig: AppConfigService) => ({
                resourceServer: appConfig.getConfig().auth.resourceServer
            })
        },
        {
            multi: true,
            provide: HTTP_INTERCEPTORS,
            useClass: AuthorizationInterceptor
        }
    ],
    bootstrap: [AppComponent]
})
export class AppModule {}
