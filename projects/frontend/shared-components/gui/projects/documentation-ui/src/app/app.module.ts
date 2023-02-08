import { NgModule } from '@angular/core';
import { HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { AuthConfig, OAuthModule, OAuthStorage } from 'angular-oauth2-oidc';

import { ClarityModule } from '@clr/angular';

import { VmwComponentsModule } from '@vdk/shared';

import { TaurusSharedCoreModule, TaurusSharedFeaturesModule, TaurusSharedNgRxModule } from '@vdk/shared';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AuthorizationInterceptor } from './http.interceptor';
import { authCodeFlowConfig } from './auth';

@NgModule({
    imports: [
        AppRoutingModule,
        BrowserModule,
        ClarityModule,
        BrowserAnimationsModule,
        TaurusSharedCoreModule.forRoot(),
        TaurusSharedFeaturesModule.forRoot(),
        TaurusSharedNgRxModule.forRootWithDevtools(),
        VmwComponentsModule.forRoot(),
        HttpClientModule,
        OAuthModule.forRoot({
            resourceServer: {
                allowedUrls: [
                    authCodeFlowConfig.issuer,
                    '/metadata'
                ],
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
export class AppModule {
}
