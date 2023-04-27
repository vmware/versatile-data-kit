/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CUSTOM_ELEMENTS_SCHEMA, ViewContainerRef } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfirmationContainerComponent } from './confirmation-container.component';

describe('ConfirmationContainerComponent', () => {
    let component: ConfirmationContainerComponent;
    let fixture: ComponentFixture<ConfirmationContainerComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [BrowserModule],
            declarations: [ConfirmationContainerComponent],
            schemas: [CUSTOM_ELEMENTS_SCHEMA]
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(ConfirmationContainerComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should verify component is created', () => {
        // Then
        expect(component).toBeTruthy();
    });

    describe('Properties::', () => {
        describe('|viewContainerRef|', () => {
            it('should verify value is populate after component is created', () => {
                // Then
                expect(component.viewContainerRef).toBeInstanceOf(ViewContainerRef);
            });
        });

        describe('|opened|', () => {
            it('should verify value is false', () => {
                // Then
                expect(component.open).toBeFalse();
            });
        });
    });
});
