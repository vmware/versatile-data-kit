/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ExecutionsTimelineComponent } from './executions-timeline.component';

import {
    DATA_PIPELINES_CONFIGS,
    DataJobExecution,
    DataJobExecutionType,
} from '../../../model';

describe('ExecutionsTimelineComponent', () => {
    let component: ExecutionsTimelineComponent;
    let fixture: ComponentFixture<ExecutionsTimelineComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [ExecutionsTimelineComponent],
            providers: [
                {
                    provide: DATA_PIPELINES_CONFIGS,
                    useFactory: () => ({
                        defaultOwnerTeamName: 'all',
                        manageConfig: {
                            allowKeyTabDownloads: true,
                            allowExecuteNow: true,
                        },
                        healthStatusUrl: 'baseUrl',
                    }),
                },
            ],
        }).compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(ExecutionsTimelineComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should create', () => {
        const mockExec = {
            /* eslint-disable-next-line @typescript-eslint/naming-convention */
            startedBy: 'manual/auser',
        } as DataJobExecution;
        expect(component.getManualExecutedByTitle(mockExec)).toBe(
            ExecutionsTimelineComponent.manualRunKnownUser + ' auser',
        );

        mockExec.startedBy = 'manual/manual';
        mockExec.type = DataJobExecutionType.MANUAL;
        expect(component.getManualExecutedByTitle(mockExec)).toBe(
            ExecutionsTimelineComponent.manualRunKnownUser + ' manual',
        );

        mockExec.startedBy = 'scheduled/runtime';
        mockExec.type = DataJobExecutionType.SCHEDULED;
        expect(component.getManualExecutedByTitle(mockExec)).toContain(
            ExecutionsTimelineComponent.manualRunNoUser,
        );

        mockExec.startedBy = 'scheduled/runtime';
        mockExec.type = null;
        expect(component.getManualExecutedByTitle(mockExec)).toContain(
            ExecutionsTimelineComponent.manualRunNoUser,
        );
    });

    describe('Methods::', () => {
        // TODO write some unit tests
        it('no-op', () => {
            // No-op.
            expect(true).toBeTrue();
        });
    });
});
