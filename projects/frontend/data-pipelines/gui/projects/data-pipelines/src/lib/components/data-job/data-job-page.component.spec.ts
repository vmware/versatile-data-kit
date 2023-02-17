/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';

import { BehaviorSubject, of, Subject } from 'rxjs';

import {
    ComponentModel,
    ComponentService,
    ComponentStateImpl,
    createRouteSnapshot,
    ErrorHandlerService,
    NavigationService,
    RouterService,
    RouterState,
    RouteState,
    ToastService
} from '@vdk/shared';

import {
    DATA_PIPELINES_CONFIGS,
    DataJobDeploymentDetails,
    DataJobDeploymentStatus,
    DataJobDetails,
    DataJobExecution,
    DataJobExecutionStatus,
    DataJobExecutionType
} from '../../model';

import { DataJobsApiService, DataJobsService } from '../../services';

import { DataJobPageComponent } from './data-job-page.component';

describe('DataJobsDetailsComponent', () => {
    let componentServiceStub: jasmine.SpyObj<ComponentService>;
    let navigationServiceStub: jasmine.SpyObj<NavigationService>;
    let routerServiceStub: jasmine.SpyObj<RouterService>;
    let toastServiceStub: jasmine.SpyObj<ToastService>;
    let dataJobsApiServiceStub: jasmine.SpyObj<DataJobsApiService>;
    let dataJobsServiceStub: jasmine.SpyObj<DataJobsService>;
    let errorHandlerServiceStub: jasmine.SpyObj<ErrorHandlerService>;

    let componentModelStub: ComponentModel;
    let component: DataJobPageComponent;
    let fixture: ComponentFixture<DataJobPageComponent>;

    const TEST_JOB_EXECUTION = {
        id: 'id002',
        jobName: 'job002',
        status: DataJobExecutionStatus.SUBMITTED,
        startTime: new Date().toISOString(),
        startedBy: 'aUserov',
        endTime: new Date().toISOString(),
        type: DataJobExecutionType.MANUAL,
        opId: 'op002',
        message: 'message001',
        deployment: {
            id: 'id002',
            enabled: true,
            jobVersion: '002',
            mode: 'test_mode',
            vdkVersion: '002',
            resources: {
                memoryLimit: 1000,
                memoryRequest: 1000,
                cpuLimit: 0.5,
                cpuRequest: 0.5
            },
            executions: [],
            deployedDate: '2020-11-11T10:10:10Z',
            deployedBy: 'pmitev',
            status: DataJobDeploymentStatus.SUCCESS
        }
    } as DataJobExecution;

    const TEST_JOB_DEPLOYMENT = {
        id: 'id002',
        enabled: true,
        /* eslint-disable-next-line @typescript-eslint/naming-convention */
        job_version: '002',
        mode: 'test_mode',
        /* eslint-disable-next-line @typescript-eslint/naming-convention */
        vdk_version: '002',
        endTime: new Date(),
        opId: 'op002',
        message: 'message002',
        /* eslint-disable @typescript-eslint/naming-convention */
        deployed_date: '2020-11-11T10:10:10Z',
        deployed_by: 'pmitev',
        resources: {
            memory_limit: 1000,
            memory_request: 1000,
            cpu_limit: 0.5,
            cpu_request: 0.5
        }
        /* eslint-enable @typescript-eslint/naming-convention */

    } as DataJobDeploymentDetails;

    beforeEach(() => {
        componentServiceStub = jasmine.createSpyObj<ComponentService>('componentService', ['init', 'getModel', 'idle']);
        navigationServiceStub = jasmine.createSpyObj<NavigationService>('navigationService', ['navigate', 'navigateTo', 'navigateBack']);
        routerServiceStub = jasmine.createSpyObj<RouterService>('routerService', ['getState']);
        toastServiceStub = jasmine.createSpyObj<ToastService>('toastService', ['show']);
        dataJobsApiServiceStub = jasmine.createSpyObj<DataJobsApiService>('dataJobsApiService', [
            'getJobDetails',
            'getJobExecutions',
            'getJobDeployments',
            'removeJob',
            'downloadFile',
            'executeDataJob',
            'getJob'
        ]);
        dataJobsServiceStub = jasmine.createSpyObj<DataJobsService>('dataJobsService', [
            'loadJobs',
            'notifyForRunningJobExecutionId',
            'notifyForJobExecutions',
            'notifyForTeamImplicitly',
            'getNotifiedForRunningJobExecutionId',
            'getNotifiedForJobExecutions',
            'getNotifiedForTeamImplicitly'
        ]);
        errorHandlerServiceStub = jasmine.createSpyObj<ErrorHandlerService>('errorHandlerService', [
            'processError',
            'handleError'
        ]);

        const activatedRouteStub = () => ({
            snapshot: createRouteSnapshot({
                data: {
                    activateSubpageNavigation: true
                }
            })
        });

        dataJobsApiServiceStub.executeDataJob.and.returnValue(new Subject());
        dataJobsApiServiceStub.getJob.and.returnValue(new Subject());
        dataJobsApiServiceStub.getJobDetails.and.returnValue(new Subject());
        dataJobsApiServiceStub.getJobExecutions.and.returnValue(of({ content: [TEST_JOB_EXECUTION], totalItems: 1, totalPages: 1 }));
        dataJobsApiServiceStub.getJobDeployments.and.returnValue(of([TEST_JOB_DEPLOYMENT]));
        dataJobsApiServiceStub.removeJob.and.returnValue(new Subject());
        dataJobsApiServiceStub.downloadFile.and.returnValue(new Subject());

        dataJobsServiceStub.getNotifiedForRunningJobExecutionId.and.returnValue(new Subject());
        dataJobsServiceStub.getNotifiedForJobExecutions.and.returnValue(new Subject());
        dataJobsServiceStub.getNotifiedForTeamImplicitly.and.returnValue(new BehaviorSubject('taurus'));

        TestBed.configureTestingModule({
            imports: [
                RouterTestingModule.withRoutes([])
            ],
            schemas: [NO_ERRORS_SCHEMA],
            declarations: [DataJobPageComponent],
            providers: [
                { provide: ComponentService, useValue: componentServiceStub },
                { provide: NavigationService, useValue: navigationServiceStub },
                { provide: RouterService, useValue: routerServiceStub },
                { provide: ActivatedRoute, useFactory: activatedRouteStub },
                { provide: ToastService, useValue: toastServiceStub },
                { provide: DataJobsApiService, useValue: dataJobsApiServiceStub },
                { provide: DataJobsService, useValue: dataJobsServiceStub },
                { provide: ErrorHandlerService, useValue: errorHandlerServiceStub },
                {
                    provide: DATA_PIPELINES_CONFIGS,
                    useFactory: () => ({
                        defaultOwnerTeamName: 'all',
                        manageConfig: {
                            allowKeyTabDownloads: true,
                            allowExecuteNow: true
                        }
                    })
                }
            ]
        });

        componentModelStub = ComponentModel.of(
            ComponentStateImpl.of({}),
            RouterState.of(
                RouteState.empty(),
                1
            )
        );
        componentServiceStub.init.and.returnValue(of(componentModelStub));
        componentServiceStub.getModel.and.returnValue(of(componentModelStub));
        routerServiceStub.getState.and.returnValue(of(RouteState.empty()));

        fixture = TestBed.createComponent(DataJobPageComponent);
        component = fixture.componentInstance;
        component.model = componentModelStub;
    });

    it('can load instance', () => {
        expect(component).toBeTruthy();
    });

    describe('ngOnInit', () => {
        it('makes expected calls', () => {
            // When
            component.ngOnInit();

            // Then
            expect(componentServiceStub.init).toHaveBeenCalled();
            expect(componentServiceStub.getModel).toHaveBeenCalled();
            expect(routerServiceStub.getState).toHaveBeenCalled();
        });
    });

    describe('allowJobExecuteNow', () => {
        it('returns true in case of dataPipelinesModuleConfig.manageConfig.allowExecuteNow', () => {
            expect(component.isExecuteJobAllowed).toBeFalse();
        });
    });

    describe('confirmExecuteJob', () => {
        it('makes expected calls', () => {
            // When
            // @ts-ignore
            spyOn(component, '_submitOperationStarted').and.callThrough();
            // @ts-ignore
            spyOn(component, '_extractJobDeployment').and.returnValue({ id: '10' } as DataJobDetails);

            // When
            component.confirmExecuteJob();

            // Then
            expect(dataJobsApiServiceStub.executeDataJob).toHaveBeenCalled();
            // @ts-ignore
            expect(component._submitOperationStarted).toHaveBeenCalled();
        });
    });

    describe('executeJob', () => {
        it('sets executeNowOptions', () => {
            // When
            component.executeJob();

            // Then
            expect(component.executeNowOptions.message).toBeDefined();
            expect(component.executeNowOptions.infoText).toBeDefined();
            expect(component.executeNowOptions.opened).toBeTrue();
            expect(component.executeNowOptions.title).toBeDefined();
        });
    });

    describe('downloadKey', () => {
        it('makes expected calls', () => {
            // Given
            // @ts-ignore
            spyOn(component, '_submitOperationStarted').and.callThrough();

            // When
            component.downloadJobKey();

            // Then
            // @ts-ignore
            expect(component._submitOperationStarted).toHaveBeenCalled();
            expect(dataJobsApiServiceStub.downloadFile).toHaveBeenCalled();
        });
    });

    describe('confirmRemoveJob', () => {
        it('makes expected calls', () => {
            // Given
            // @ts-ignore
            spyOn(component, '_submitOperationStarted').and.callThrough();

            // When
            component.confirmRemoveJob();

            // Then
            // @ts-ignore
            expect(component._submitOperationStarted).toHaveBeenCalled();
            expect(dataJobsApiServiceStub.removeJob).toHaveBeenCalled();
        });
    });

    describe('removeJob', () => {
        it('sets deleteOptions', () => {
            // When
            component.removeJob();

            // Then
            expect(component.deleteOptions.message).toBeDefined();
            expect(component.deleteOptions.infoText).toBeDefined();
            expect(component.deleteOptions.showOkBtn).toBeTrue();
            expect(component.deleteOptions.cancelBtn).toBeDefined();
            expect(component.deleteOptions.opened).toBeTrue();
        });
    });
});
