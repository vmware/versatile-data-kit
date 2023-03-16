/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';

import { OAuthModule } from 'angular-oauth2-oidc';

import { AppComponent } from './app.component';

describe('AppComponent', () => {
    let component: AppComponent;
    let fixture: ComponentFixture<AppComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [AppComponent],
            schemas: [CUSTOM_ELEMENTS_SCHEMA],
            imports: [OAuthModule.forRoot(), HttpClientTestingModule]
        })
            .compileComponents()
            .then(() => {
                fixture = TestBed.createComponent(AppComponent);
                component = fixture.debugElement.componentInstance;
            });
    });

    it('should create the app', () => {
        expect(component).toBeTruthy();
    });
});
