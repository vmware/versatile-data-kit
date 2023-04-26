/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NO_ERRORS_SCHEMA } from '@angular/core';
import { FormBuilder } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';

import { BehaviorSubject, of, Subject } from 'rxjs';

import {
    ComponentModel,
    ComponentService,
    ComponentStateImpl,
    ErrorHandlerService,
    FORM_STATE,
    generateErrorCodes,
    NavigationService,
    RouterService,
    RouterState,
    RouteState,
    ToastService,
    UrlOpenerService,
    VdkFormState
} from '@versatiledatakit/shared';

import { DataJobsApiService, DataJobsService } from '../../../../services';

import { ExtractContactsPipe, ExtractJobStatusPipe, FormatSchedulePipe } from '../../../../shared/pipes';

import {
    DATA_PIPELINES_CONFIGS,
    DataJob,
    DataJobDeploymentDetails,
    DataJobDeploymentStatus,
    DataJobDetails,
    DataJobExecution,
    DataJobExecutionsPage,
    DataJobExecutionStatus,
    DataJobExecutionType
} from '../../../../model';

import { LOAD_JOB_ERROR_CODES } from '../../../../state/error-codes';

import { TASK_LOAD_JOB_DETAILS, TASK_LOAD_JOB_STATE } from '../../../../state/tasks';

import { DataJobDetailsPageComponent } from './data-job-details-page.component';

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
    id: 'id001',
    enabled: true,
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    job_version: '001',
    mode: 'test_mode',
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    vdk_version: '001'
} as DataJobDeploymentDetails;

const TEST_JOB_DETAILS = {
    /* eslint-disable-next-line @typescript-eslint/naming-convention */
    job_name: 'job001',
    team: 'taurus',
    description: 'description'
};

describe('DataJobsDetailsModalComponent', () => {
    let componentServiceStub: jasmine.SpyObj<ComponentService>;
    let navigationServiceStub: jasmine.SpyObj<NavigationService>;
    let activatedRouteStub: ActivatedRoute;
    let routerServiceStub: jasmine.SpyObj<RouterService>;
    let toastServiceStub: jasmine.SpyObj<ToastService>;
    let dataJobsApiServiceStub: jasmine.SpyObj<DataJobsApiService>;
    let dataJobsServiceStub: jasmine.SpyObj<DataJobsService>;
    let errorHandlerServiceStub: jasmine.SpyObj<ErrorHandlerService>;
    let urlOpenerServiceStub: jasmine.SpyObj<UrlOpenerService>;

    let componentModelStub: ComponentModel;
    let component: DataJobDetailsPageComponent;
    let fixture: ComponentFixture<DataJobDetailsPageComponent>;

    beforeEach(() => {
        componentServiceStub = jasmine.createSpyObj<ComponentService>('componentService', ['init', 'getModel', 'idle', 'update']);
        navigationServiceStub = jasmine.createSpyObj<NavigationService>('navigationService', ['navigateTo', 'navigateBack']);
        activatedRouteStub = { snapshot: null } as any;
        routerServiceStub = jasmine.createSpyObj<RouterService>('routerService', ['getState']);
        toastServiceStub = jasmine.createSpyObj<ToastService>('toastService', ['show']);
        dataJobsApiServiceStub = jasmine.createSpyObj<DataJobsApiService>('dataJobsApiService', [
            'getJobDetails',
            'getJobExecutions',
            'getJobDeployments',
            'downloadFile',
            'updateDataJobStatus',
            'updateDataJob',
            'executeDataJob',
            'removeJob',
            'getJob'
        ]);
        dataJobsServiceStub = jasmine.createSpyObj<DataJobsService>('dataJobsService', [
            'loadJobs',
            'loadJob',
            'notifyForRunningJobExecutionId',
            'notifyForJobExecutions',
            'notifyForTeamImplicitly',
            'getNotifiedForRunningJobExecutionId',
            'getNotifiedForJobExecutions',
            'getNotifiedForTeamImplicitly'
        ]);
        errorHandlerServiceStub = jasmine.createSpyObj<ErrorHandlerService>('errorHandlerService', ['processError', 'handleError']);
        urlOpenerServiceStub = jasmine.createSpyObj<UrlOpenerService>('urlOpenerServiceStub', ['open']);

        dataJobsApiServiceStub.getJobDetails.and.returnValue(new BehaviorSubject<DataJobDetails>(TEST_JOB_DETAILS).asObservable());
        dataJobsApiServiceStub.getJobExecutions.and.returnValue(
            new BehaviorSubject<DataJobExecutionsPage>({
                content: [TEST_JOB_EXECUTION],
                totalItems: 1,
                totalPages: 1
            }).asObservable()
        );
        dataJobsApiServiceStub.getJobDeployments.and.returnValue(
            new BehaviorSubject<DataJobDeploymentDetails[]>([TEST_JOB_DEPLOYMENT]).asObservable()
        );
        dataJobsApiServiceStub.downloadFile.and.returnValue(new BehaviorSubject<Blob>({} as never).asObservable());
        dataJobsApiServiceStub.updateDataJobStatus.and.returnValue(
            new BehaviorSubject<{ enabled: boolean }>({
                enabled: true
            }).asObservable()
        );
        dataJobsApiServiceStub.updateDataJob.and.returnValue(new BehaviorSubject<DataJobDetails>({}).asObservable());
        dataJobsApiServiceStub.executeDataJob.and.returnValue(new BehaviorSubject<undefined>(undefined).asObservable());
        dataJobsApiServiceStub.removeJob.and.returnValue(new BehaviorSubject<DataJobDetails>(TEST_JOB_DETAILS).asObservable());
        dataJobsApiServiceStub.getJob.and.returnValue(of({ data: { content: [TEST_JOB_DETAILS] } } as DataJob));

        dataJobsServiceStub.getNotifiedForJobExecutions.and.returnValue(new Subject());
        dataJobsServiceStub.getNotifiedForTeamImplicitly.and.returnValue(new BehaviorSubject(TEST_JOB_DETAILS.team));

        componentModelStub = ComponentModel.of(ComponentStateImpl.of({}), RouterState.of(RouteState.empty(), 1));
        routerServiceStub.getState.and.returnValue(new Subject());
        componentServiceStub.init.and.returnValue(of(componentModelStub));
        componentServiceStub.getModel.and.returnValue(of(componentModelStub));

        navigationServiceStub.navigateBack.and.returnValue(Promise.resolve(true));

        generateErrorCodes<DataJobsApiService>(dataJobsApiServiceStub, ['getJob', 'getJobDetails']);

        LOAD_JOB_ERROR_CODES[TASK_LOAD_JOB_STATE] = dataJobsApiServiceStub.errorCodes.getJob;
        LOAD_JOB_ERROR_CODES[TASK_LOAD_JOB_DETAILS] = dataJobsApiServiceStub.errorCodes.getJobDetails;

        TestBed.configureTestingModule({
            schemas: [NO_ERRORS_SCHEMA],
            declarations: [DataJobDetailsPageComponent, FormatSchedulePipe, ExtractJobStatusPipe, ExtractContactsPipe],
            imports: [RouterTestingModule],
            providers: [
                FormBuilder,
                { provide: RouterService, useValue: routerServiceStub },
                { provide: ComponentService, useValue: componentServiceStub },
                { provide: NavigationService, useValue: navigationServiceStub },
                { provide: ActivatedRoute, useValue: activatedRouteStub },
                {
                    provide: DataJobsApiService,
                    useValue: dataJobsApiServiceStub
                },
                { provide: ToastService, useValue: toastServiceStub },
                { provide: DataJobsService, useValue: dataJobsServiceStub },
                {
                    provide: ErrorHandlerService,
                    useValue: errorHandlerServiceStub
                },
                { provide: UrlOpenerService, useValue: urlOpenerServiceStub },
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

        fixture = TestBed.createComponent(DataJobDetailsPageComponent);
        component = fixture.componentInstance;
        component.jobDetails = TEST_JOB_DETAILS;
        component.jobExecutions = [TEST_JOB_EXECUTION];
        component.model = componentModelStub;
    });

    it('can load instance', () => {
        expect(component).toBeTruthy();
    });

    it(`readOnly has default value`, () => {
        expect(component.isJobEditable).toBeFalse();
    });

    it(`loadingExecutions has default value`, () => {
        expect(component.loadingExecutions).toBeTrue();
    });

    it(`canEditSection has default value`, () => {
        expect(component.canEditSection).toBeTrue();
    });

    it(`readOnly sets readFormState as formState`, () => {
        component.isJobEditable = false;
        component.ngOnInit();

        expect(component.formState).toEqual(component.readFormState);
    });

    describe('isDescriptionSubmitEnabled', () => {
        it('returns false', () => {
            expect(component.isDescriptionSubmitEnabled()).toBeFalse();
        });
    });

    describe('isStatusSubmitEnabled', () => {
        it('returns false', () => {
            expect(component.isStatusSubmitEnabled()).toBeFalse();
        });
    });

    describe('_resetJobDetails', () => {
        it('do not reset valid job', () => {
            // @ts-ignore
            component._resetJobDetails();
            expect(component.jobDetails).toEqual(TEST_JOB_DETAILS);
        });

        it('do reset invalid job', () => {
            component.jobDetails = null;
            // @ts-ignore
            component._resetJobDetails();
            expect(component.jobDetails).toBeDefined();
        });
    });

    describe('sectionStateChange', () => {
        it('makes expected calls for FORM_STATE.SUBMIT', () => {
            const vMWFormStateStub = {} as VdkFormState;
            vMWFormStateStub.state = FORM_STATE.SUBMIT;

            spyOn(component, 'submitForm').and.callThrough();
            component.sectionStateChange(vMWFormStateStub);
            expect(component.submitForm).toHaveBeenCalled();
        });
    });

    describe('sectionStateChange', () => {
        it('makes expected calls for FORM_STATE.CAN_EDIT', () => {
            const vMWFormStateStub = {} as VdkFormState;
            vMWFormStateStub.state = FORM_STATE.CAN_EDIT;
            component.sectionStateChange(vMWFormStateStub);
            expect(component.canEditSection).toBeTrue();
        });
    });

    describe('sectionStateChange', () => {
        it('makes expected calls for FORM_STATE.EDIT', () => {
            const vMWFormStateStub = {} as VdkFormState;
            vMWFormStateStub.state = FORM_STATE.EDIT;

            component.sectionStateChange(vMWFormStateStub);
            expect(component.canEditSection).toBeFalse();
        });
    });

    describe('doSubmit', () => {
        it('makes expected calls for emittingSection description', () => {
            const vMWFormStateStub = {} as VdkFormState;
            vMWFormStateStub.emittingSection = 'description';

            spyOn(component, 'isDescriptionSubmitEnabled').and.callThrough();
            component.submitForm(vMWFormStateStub);
            expect(component.isDescriptionSubmitEnabled).toHaveBeenCalled();
        });

        it('makes expected calls for emittingSection status', () => {
            const vMWFormStateStub = {} as VdkFormState;
            vMWFormStateStub.emittingSection = 'status';

            spyOn(component, 'isStatusSubmitEnabled').and.callThrough();
            component.submitForm(vMWFormStateStub);
            expect(component.isStatusSubmitEnabled).toHaveBeenCalled();
        });
    });

    describe('ngOnInit', () => {
        it('makes expected calls', () => {
            routerServiceStub.getState.and.returnValue(of(RouteState.empty()));
            component.ngOnInit();

            expect(dataJobsServiceStub.loadJob).toHaveBeenCalled();
        });
    });

    describe('editOperationEnded', () => {
        it('sets expected states', () => {
            component.editOperationEnded();
            expect(component.formState.state).toEqual(FORM_STATE.CAN_EDIT);
            expect(component.canEditSection).toBeTrue();
        });
    });
});
