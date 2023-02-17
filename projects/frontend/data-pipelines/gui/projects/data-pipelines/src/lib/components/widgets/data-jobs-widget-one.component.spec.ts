/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';

import { ErrorHandlerService } from '@vdk/shared';

import { FormatSchedulePipe } from '../../shared/pipes';

import { DataJobsApiService } from '../../services';

import { DataJobsWidgetOneComponent, WidgetTab } from './data-jobs-widget-one.component';

describe('DataJobsWidgetOneComponent', () => {
    let errorHandlerServiceStub: jasmine.SpyObj<ErrorHandlerService>;

    let component: DataJobsWidgetOneComponent;
    let fixture: ComponentFixture<DataJobsWidgetOneComponent>;

    beforeEach(async () => {
        // mock service
        const dataJobsServiceStub = () => ({
            getJobs: () => of({
                data: {
                    totalItems: 1, totalPages: 11, content: [
                        {
                            jobName: 'test-job',
                            item: { config: { schedule: { scheduleCron: '*/5 * * * *' } } }
                        }
                    ]
                }
            })
        });
        errorHandlerServiceStub = jasmine.createSpyObj<ErrorHandlerService>('errorHandlerService', [
            'processError',
            'handleError'
        ]);

        await TestBed.configureTestingModule({
            declarations: [DataJobsWidgetOneComponent, FormatSchedulePipe],
            providers: [
                { provide: DataJobsApiService, useFactory: dataJobsServiceStub },
                { provide: ErrorHandlerService, useValue: errorHandlerServiceStub }
            ]
        })
                     .compileComponents();
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(DataJobsWidgetOneComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('can load instance', () => {
        expect(component).toBeTruthy();
    });

    describe('ngOnInit', () => {
        it('make expected calls', () => {
            const dataJobsServiceStub: DataJobsApiService = fixture.debugElement.injector.get(
                DataJobsApiService
            );
            spyOn(dataJobsServiceStub, 'getJobs').and.callThrough();
            component.ngOnInit();
            expect(dataJobsServiceStub.getJobs).toHaveBeenCalled();

            // TODO: make expected calls to executions & failures
        });
    });

    describe('switchTab', () => {
        it('switch to expected tab', () => {
            component.switchTab(WidgetTab.EXECUTIONS);
            expect(component.selectedTab).toEqual(WidgetTab.EXECUTIONS);
            expect(component.currentPage).toEqual(1);
        });

        it('collapse panel when click the same selected tab', () => {
            component.switchTab(WidgetTab.EXECUTIONS);
            component.switchTab(WidgetTab.EXECUTIONS);
            expect(component.selectedTab).toEqual(WidgetTab.NONE);
        });
    });

    describe('handle errors', () => {
        it('should catch error when API fails', () => {
            expect(component.errorJobs).toEqual(false);
            const dataJobsServiceStub: DataJobsApiService = fixture.debugElement.injector.get(
                DataJobsApiService
            );
            spyOn(dataJobsServiceStub, 'getJobs').and.returnValue(throwError(() => true));
            component.refresh(1, WidgetTab.DATAJOBS);

            component.jobs$.subscribe();
            component.executions$.subscribe();
            component.failures$.subscribe();

            expect(component.errorJobs).toEqual(true);

            // TODO: handle errors for executions & failures
        });
    });
});
