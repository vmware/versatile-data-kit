/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ExtractJobStatusPipe } from '../../../pipes/extract-job-status.pipe';

import { StatusPanelComponent } from './status-panel.component';

describe('StatusPanelComponent', () => {
    let component: StatusPanelComponent;
    let fixture: ComponentFixture<StatusPanelComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [StatusPanelComponent, ExtractJobStatusPipe]
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(StatusPanelComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
