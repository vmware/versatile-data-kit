/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { waitForAsync, ComponentFixture, TestBed } from '@angular/core/testing';
import { GettingStartedComponent } from './getting-started.component';
import { OAuthService } from 'angular-oauth2-oidc';
import { AppConfigService } from '../app-config.service';

describe('GettingStartedComponent', () => {
    let component: GettingStartedComponent;
    let fixture: ComponentFixture<GettingStartedComponent>;
    let appConfigServiceStub: jasmine.SpyObj<AppConfigService>;

    beforeEach(waitForAsync(() => {
        appConfigServiceStub = jasmine.createSpyObj<AppConfigService>('appConfigService', ['getConfig', 'getAuthCodeFlowConfig']);
        TestBed.configureTestingModule({
            declarations: [GettingStartedComponent],
            providers: [OAuthService, { provide: AppConfigService, useValue: appConfigServiceStub }],
            imports: []
        }).compileComponents();
    }));

    it('should create without ignored components', () => {
        appConfigServiceStub.getConfig.and.returnValue({
            auth: {},
            ignoreRoutes: [],
            ignoreComponents: []
        });

        fixture = TestBed.createComponent(GettingStartedComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();

        expect(component).toBeTruthy();
        expect(component.widgetsVisible).toBeTrue();
    });

    it('should create with widgets component ignored', () => {
        appConfigServiceStub.getConfig.and.returnValue({
            auth: {},
            ignoreRoutes: [],
            ignoreComponents: ['widgetsComponent']
        });

        fixture = TestBed.createComponent(GettingStartedComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();

        expect(component).toBeTruthy();
        expect(component.widgetsVisible).toBeFalse();
    });
});
