/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { DataJobsManagePageComponent } from './data-jobs-manage-page.component';

describe('DataJobsManageComponent', () => {
    let component: DataJobsManagePageComponent;
    let fixture: ComponentFixture<DataJobsManagePageComponent>;

    beforeEach(() => {
        TestBed.configureTestingModule({
            schemas: [NO_ERRORS_SCHEMA],
            declarations: [DataJobsManagePageComponent]
        });
        fixture = TestBed.createComponent(DataJobsManagePageComponent);
        component = fixture.componentInstance;
    });

    it('can load instance', () => {
        expect(component).toBeTruthy();
    });
});
