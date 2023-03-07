/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NO_ERRORS_SCHEMA } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Location } from '@angular/common';
import {
    ComponentFixture,
    fakeAsync,
    TestBed,
    tick,
} from '@angular/core/testing';

import { of, Subject } from 'rxjs';

import { ClrDatagridStateInterface } from '@clr/angular';

import {
    ASC,
    CallFake,
    ComponentModel,
    ComponentService,
    ComponentStateImpl,
    DESC,
    ErrorHandlerService,
    NavigationService,
    RouterService,
    RouterState,
    RouteState,
    ToastService,
} from '@versatiledatakit/shared';

import { ExtractJobStatusPipe } from '../../../../shared/pipes';

import { DataJobsApiService, DataJobsService } from '../../../../services';

import { DATA_PIPELINES_CONFIGS, DisplayMode } from '../../../../model';

import { DataJobsManageGridComponent } from './data-jobs-manage-grid.component';

describe('DataJobsManageGridComponent', () => {
    let componentServiceStub: jasmine.SpyObj<ComponentService>;
    let navigationServiceStub: jasmine.SpyObj<NavigationService>;
    let routerServiceStub: jasmine.SpyObj<RouterService>;
    let dataJobsServiceStub: jasmine.SpyObj<DataJobsService>;
    let toastServiceStub: jasmine.SpyObj<ToastService>;
    let errorHandlerServiceStub: jasmine.SpyObj<ErrorHandlerService>;

    let componentModelStub: ComponentModel;
    let component: DataJobsManageGridComponent;
    let fixture: ComponentFixture<DataJobsManageGridComponent>;

    const TEST_DEPLOYMENT = {
        id: 'id001',
        enabled: true,
    };

    const TEST_JOB = {
        jobName: 'job001',
        config: {
            description: 'description001',
            team: 'testTeam',
        },
        deployments: [TEST_DEPLOYMENT],
    };

    let teamSubject: Subject<string>;
    let teamSubjectSubscribeSpy: jasmine.Spy;

    const EMPTY_TEAM_NAME_FILTER = '';

    beforeAll(() => {
        // This hack is needed in order to prevent tests to reload browser.
        // Browser reloading stops Tests execution in the same browser, and need to restart execution from beginning.
        window.onbeforeunload = () => 'Stop browser from reload!';
    });

    beforeEach(() => {
        componentServiceStub = jasmine.createSpyObj<ComponentService>(
            'componentService',
            ['init', 'getModel', 'idle', 'update'],
        );
        navigationServiceStub = jasmine.createSpyObj<NavigationService>(
            'navigationService',
            ['navigateTo', 'navigateBack'],
        );
        routerServiceStub = jasmine.createSpyObj<RouterService>(
            'routerService',
            ['getState', 'get'],
        );
        dataJobsServiceStub = jasmine.createSpyObj<DataJobsService>(
            'dataJobsService',
            [
                'loadJobs',
                'notifyForRunningJobExecutionId',
                'notifyForJobExecutions',
                'notifyForTeamImplicitly',
                'getNotifiedForRunningJobExecutionId',
                'getNotifiedForJobExecutions',
                'getNotifiedForTeamImplicitly',
            ],
        );
        toastServiceStub = jasmine.createSpyObj<ToastService>('toastService', [
            'show',
        ]);
        errorHandlerServiceStub = jasmine.createSpyObj<ErrorHandlerService>(
            'errorHandlerService',
            ['processError', 'handleError'],
        );

        teamSubject = new Subject<string>();
        teamSubjectSubscribeSpy = spyOn(
            teamSubject,
            'subscribe',
        ).and.callThrough();

        const activatedRouteStub = () => ({
            queryParams: {
                subscribe: CallFake,
            },
            snapshot: null,
        });
        const dataJobsApiServiceStub = () => ({
            getAllJobs: () => ({
                subscribe: CallFake,
            }),
            getJobDetails: () => ({
                subscribe: () => CallFake,
            }),
            getJobExecutions: () => ({
                subscribe: () => CallFake,
            }),
            updateDataJobStatus: () => ({
                subscribe: () => {
                    return new Subject();
                },
            }),
            executeDataJob: () => ({
                subscribe: () => {
                    return new Subject();
                },
            }),
        });
        const locationStub = () => ({
            path: () => 'Test',
            go: () => CallFake,
        });
        const routerStub = () => ({
            url: '/explore/data-jobs',
        });

        TestBed.configureTestingModule({
            schemas: [NO_ERRORS_SCHEMA],
            declarations: [DataJobsManageGridComponent, ExtractJobStatusPipe],
            providers: [
                {
                    provide: DATA_PIPELINES_CONFIGS,
                    useFactory: () => ({
                        defaultOwnerTeamName: 'all',
                        manageConfig: {
                            filterByTeamName: true,
                            showTeamsColumn: true,
                            allowExecuteNow: true,
                            displayMode: DisplayMode.COMPACT,
                            selectedTeamNameObservable: teamSubject,
                        },
                    }),
                },
                { provide: RouterService, useValue: routerServiceStub },
                { provide: ComponentService, useValue: componentServiceStub },
                { provide: NavigationService, useValue: navigationServiceStub },
                { provide: ActivatedRoute, useFactory: activatedRouteStub },
                { provide: DataJobsService, useValue: dataJobsServiceStub },
                { provide: ToastService, useValue: toastServiceStub },
                {
                    provide: DataJobsApiService,
                    useFactory: dataJobsApiServiceStub,
                },
                { provide: Location, useFactory: locationStub },
                { provide: Router, useFactory: routerStub },
                {
                    provide: ErrorHandlerService,
                    useValue: errorHandlerServiceStub,
                },
            ],
        });

        componentModelStub = ComponentModel.of(
            ComponentStateImpl.of({}),
            RouterState.of(RouteState.empty(), 1),
        );
        componentServiceStub.init.and.returnValue(of(componentModelStub));
        componentServiceStub.getModel.and.returnValue(of(componentModelStub));
        routerServiceStub.getState.and.returnValue(new Subject());
        routerServiceStub.get.and.returnValue(new Subject());

        fixture = TestBed.createComponent(DataJobsManageGridComponent);
        component = fixture.componentInstance;
        component.selectedJob = TEST_JOB;
        component.model = componentModelStub;
    });

    it('can load instance', () => {
        expect(component).toBeTruthy();
    });

    describe('editJob', () => {
        it('skips editJob for undefined job', () => {
            // Given
            const navigateToSpy = spyOn(component, 'navigateTo').and.callFake(
                CallFake,
            );
            component.selectedJob = null;

            // When
            component.navigateToJobDetails();

            // Then
            expect(component.selectedJob).toBeNull();
            expect(navigateToSpy).not.toHaveBeenCalled();
        });

        it('opens editJob for valid job', () => {
            // Given
            const navigateToSpy = spyOn(
                component,
                'navigateTo',
            ).and.returnValue(Promise.resolve(true));
            component.selectedJob = null;
            component.ngOnInit();

            // When
            component.navigateToJobDetails(TEST_JOB);

            // Then
            expect(component.selectedJob).toBeDefined();
            expect(navigateToSpy).toHaveBeenCalledWith({
                '$.team': 'testTeam',
                '$.job': 'job001',
            });
        });
    });

    describe('ngOnInit', () => {
        it('makes expected calls', () => {
            component.ngOnInit();
            expect(componentServiceStub.init).toHaveBeenCalled();
            expect(componentServiceStub.getModel).toHaveBeenCalled();
        });
    });

    describe('showTeamsColumn', () => {
        it('returns correct value', () => {
            expect(component.showTeamsColumn()).toBeTrue();
        });
    });

    describe('onJobStatusChange', () => {
        it('makes expected calls for empty SelectedJobDeployment', () => {
            component.selectedJob.deployments = [];
            spyOn(component, 'extractSelectedJobDeployment').and.callThrough();
            spyOn(console, 'log').and.callThrough();
            component.onJobStatusChange();
            expect(component.extractSelectedJobDeployment).toHaveBeenCalled();
            expect(console.log).toHaveBeenCalled();
        });

        it('makes expected calls for valid SelectedJobDeployment', () => {
            component.selectedJob.deployments = [TEST_DEPLOYMENT];
            const dataJobSServiceStub: DataJobsApiService =
                fixture.debugElement.injector.get(DataJobsApiService);
            spyOn(component, 'extractSelectedJobDeployment').and.callThrough();
            spyOn(dataJobSServiceStub, 'updateDataJobStatus').and.callThrough();
            component.onJobStatusChange();
            expect(component.extractSelectedJobDeployment).toHaveBeenCalled();
            expect(dataJobSServiceStub.updateDataJobStatus).toHaveBeenCalled();
        });
    });

    describe('onExecuteDataJob', () => {
        it('makes expected calls', () => {
            component.selectedJob = TEST_JOB;
            component.selectedJob.deployments = [TEST_DEPLOYMENT];
            const dataJobSServiceStub: DataJobsApiService =
                fixture.debugElement.injector.get(DataJobsApiService);
            spyOn(component, 'extractSelectedJobDeployment').and.callThrough();
            spyOn(dataJobSServiceStub, 'executeDataJob').and.callThrough();
            component.onExecuteDataJob();
            expect(component.extractSelectedJobDeployment).toHaveBeenCalled();
            expect(dataJobSServiceStub.executeDataJob).toHaveBeenCalled();
        });
    });

    describe('executeDataJob', () => {
        it('sets the expected options', () => {
            component.executeDataJob();
            expect(component.confirmExecuteNowOptions.message).toBeDefined();
            expect(component.confirmExecuteNowOptions.infoText).toBeDefined();
            expect(component.confirmExecuteNowOptions.opened).toBeTrue();
        });
    });

    describe('enable', () => {
        it('sets the expected options', () => {
            component.enable();
            expect(component.confirmStatusOptions.message).toBeDefined();
            expect(component.confirmStatusOptions.infoText).toBeDefined();
            expect(component.confirmStatusOptions.opened).toBeTrue();
        });
    });

    describe('disable', () => {
        it('sets the expected options', () => {
            component.disable();
            expect(component.confirmStatusOptions.message).toBeDefined();
            expect(component.confirmStatusOptions.infoText).toBeDefined();
            expect(component.confirmStatusOptions.opened).toBeTrue();
        });
    });

    describe('component initialization', () => {
        it('reads manageConfig filterByTeamName properly', () => {
            expect(component.filterByTeamName).toBeTrue();
        });

        it('reads manageConfig displayMode properly', () => {
            expect(component.displayMode).toEqual(DisplayMode.COMPACT);
        });

        it('reads manageConfig selectedTeamNameObservable properly', () => {
            expect(teamSubjectSubscribeSpy).toHaveBeenCalled();
        });
    });

    describe('resetTeamNameFilter', () => {
        it('resets the TeamNameFilter', () => {
            component.resetTeamNameFilter();
            expect(component.teamNameFilter).toEqual(EMPTY_TEAM_NAME_FILTER);
        });
    });

    describe('Methods::', () => {
        describe('|loadDataWithState|', () => {
            it('should verify will append on model team filter when default team exist', fakeAsync(() => {
                // Given
                const state: ClrDatagridStateInterface = {
                    filters: null,
                    sort: null,
                    page: {
                        size: 10,
                        current: 2,
                    },
                };
                component.ngOnInit();
                teamSubject.next('teamA');

                tick(100);

                // When
                component.loadDataWithState(state);

                tick(600);

                // Then
                const filter = componentModelStub.getComponentState().filter;
                expect(filter.criteria.length).toEqual(1);
                expect(filter.criteria[0]).toEqual({
                    property: 'config.team',
                    pattern: 'teamA',
                    sort: null,
                });
            }));

            it('should verify will append on model filter and sorting and default team filter', fakeAsync(() => {
                // Given
                const state: ClrDatagridStateInterface = {
                    filters: [
                        { property: 'deployments.enabled', value: 'true' },
                    ],
                    sort: { by: 'jobName', reverse: false },
                    page: {
                        size: 10,
                        current: 2,
                    },
                };
                component.ngOnInit();
                teamSubject.next('teamB');

                tick(100);

                // When
                component.loadDataWithState(state);

                tick(600);

                // Then
                const filter = componentModelStub.getComponentState().filter;
                expect(filter.criteria).toEqual([
                    { property: 'config.team', pattern: 'teamB', sort: null },
                    {
                        property: 'deployments.enabled',
                        pattern: 'true',
                        sort: null,
                    },
                    { property: 'jobName', pattern: null, sort: ASC },
                ]);
            }));

            it('should verify will append on model filter and sorting and no default team filter', fakeAsync(() => {
                // Given
                const state: ClrDatagridStateInterface = {
                    filters: [
                        { property: 'deployments.enabled', value: 'false' },
                    ],
                    sort: { by: 'config.description', reverse: true },
                    page: {
                        size: 10,
                        current: 2,
                    },
                };
                component.filterByTeamName = false;
                component.ngOnInit();

                tick(100);

                // When
                component.loadDataWithState(state);

                tick(600);

                // Then
                const filter = componentModelStub.getComponentState().filter;
                console.log(filter.criteria);
                expect(filter.criteria).toEqual([
                    {
                        property: 'deployments.enabled',
                        pattern: 'false',
                        sort: null,
                    },
                    {
                        property: 'config.description',
                        pattern: null,
                        sort: DESC,
                    },
                ]);
            }));
        });
    });
});
