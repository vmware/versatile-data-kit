/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NO_ERRORS_SCHEMA } from '@angular/core';
import { DataJobsExplorePageComponent } from './data-jobs-explore-page.component';

describe('DataJobsExploreComponent', () => {
    let component: DataJobsExplorePageComponent;
    let fixture: ComponentFixture<DataJobsExplorePageComponent>;

    beforeEach(() => {
        TestBed.configureTestingModule({
            schemas: [NO_ERRORS_SCHEMA],
            declarations: [DataJobsExplorePageComponent]
        });
        fixture = TestBed.createComponent(DataJobsExplorePageComponent);
        component = fixture.componentInstance;
    });

    it('can load instance', () => {
        expect(component).toBeTruthy();
    });
});
