/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { QuickFiltersComponent } from './quick-filters.component';

describe('QuickFiltersComponent', () => {
    let component: QuickFiltersComponent;
    let fixture: ComponentFixture<QuickFiltersComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [QuickFiltersComponent]
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(QuickFiltersComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
