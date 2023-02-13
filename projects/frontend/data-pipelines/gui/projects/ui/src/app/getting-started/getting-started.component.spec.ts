/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { waitForAsync, ComponentFixture, TestBed } from '@angular/core/testing';
import { GettingStartedComponent } from './getting-started.component';
import { OAuthService } from 'angular-oauth2-oidc';

describe('GettingStartedComponent', () => {
    let component: GettingStartedComponent;
    let fixture: ComponentFixture<GettingStartedComponent>;

    beforeEach(waitForAsync(() => {
        TestBed.configureTestingModule({
            declarations: [GettingStartedComponent],
            providers: [OAuthService],
            imports: []
        })
               .compileComponents();
    }));

    beforeEach(() => {
        fixture = TestBed.createComponent(GettingStartedComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
