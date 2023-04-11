/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ExtractJobStatusPipe } from '../../../pipes/extract-job-status.pipe';

import { StatusCellComponent } from './status-cell.component';

const TEST_JOB = {
    jobName: 'job002',
    config: {
        description: 'description002'
    }
};

describe('StatusCellComponent', () => {
    let component: StatusCellComponent;
    let fixture: ComponentFixture<StatusCellComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [StatusCellComponent, ExtractJobStatusPipe]
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(StatusCellComponent);
        component = fixture.componentInstance;
        component.dataJob = TEST_JOB;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
