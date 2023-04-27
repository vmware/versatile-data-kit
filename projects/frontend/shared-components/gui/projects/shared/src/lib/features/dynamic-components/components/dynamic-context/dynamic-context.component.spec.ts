/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ViewContainerRef } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DynamicContextComponent } from './dynamic-context.component';

describe('DynamicContextComponent', () => {
    let component: DynamicContextComponent;
    let fixture: ComponentFixture<DynamicContextComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [DynamicContextComponent]
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(DynamicContextComponent);
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
