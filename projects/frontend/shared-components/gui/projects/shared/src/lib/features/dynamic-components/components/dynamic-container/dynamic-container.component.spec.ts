/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ViewContainerRef } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DynamicContainerComponent } from './dynamic-container.component';

describe('DynamicContainerComponent', () => {
    let component: DynamicContainerComponent;
    let fixture: ComponentFixture<DynamicContainerComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [DynamicContainerComponent]
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(DynamicContainerComponent);
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
    });
});
