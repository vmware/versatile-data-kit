/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WidgetValueComponent } from './widget-value.component';

describe('WidgetValueComponent', () => {
    let component: WidgetValueComponent;
    let fixture: ComponentFixture<WidgetValueComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [WidgetValueComponent]
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(WidgetValueComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
