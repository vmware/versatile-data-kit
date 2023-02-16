/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CoreComponent } from './core.component';

describe('CoreComponent', () => {
    let component: CoreComponent;
    let fixture: ComponentFixture<CoreComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [CoreComponent]
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(CoreComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
