/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SHARED_FEATURES_CONFIG_TOKEN } from '../../../_token';

import { WarningConfig } from '../../model';

import { WarningComponent } from './warning.component';

describe('WarningComponent', () => {
    let serviceRequestUrl: string;

    let component: WarningComponent;
    let fixture: ComponentFixture<WarningComponent>;

    beforeEach(async () => {
        serviceRequestUrl = 'https://service-url';

        await TestBed.configureTestingModule({
            declarations: [WarningComponent],
            providers: [{ provide: SHARED_FEATURES_CONFIG_TOKEN, useValue: { warning: { serviceRequestUrl } } as WarningConfig }],
            schemas: [CUSTOM_ELEMENTS_SCHEMA]
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(WarningComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    describe('Properties::', () => {
        describe('|serviceRequestUrl|', () => {
            it('should verify value is extracted from injected features config', () => {
                // Then
                expect(component.serviceRequestUrl).toEqual(serviceRequestUrl);
            });
        });
    });
});
