/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { NO_ERRORS_SCHEMA } from '@angular/core';
import { Location } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BehaviorSubject, Observable, of, Subject } from 'rxjs';

import { ClrDatagridStateInterface } from '@clr/angular';

import { ApolloQueryResult } from '@apollo/client/core';

import {
    ASC,
    CallFake,
    ComponentModel,
    ComponentService,
    ComponentStateImpl,
    ErrorHandlerService,
    NavigationService,
    RouterService,
    RouterState,
    SystemEventDispatcher,
    URLStateManager
} from '@vdk/shared';

import { DATA_PIPELINES_CONFIGS, DataJobDetails, DataJobPage, DisplayMode } from '../../../../model';

import { DataJobsApiService, DataJobsService } from '../../../../services';

import { DataJobsExploreGridComponent } from './data-jobs-explore-grid.component';
import { QUERY_PARAM_SEARCH } from '../../../base-grid/data-jobs-base-grid.component';

describe('DataJobsExploreGridComponent', () => {
    let componentServiceStub: jasmine.SpyObj<ComponentService>;
    let dataJobsApiServiceStub: jasmine.SpyObj<DataJobsApiService>;
    let locationStub: jasmine.SpyObj<Location>;
    let navigationServiceStub: jasmine.SpyObj<NavigationService>;
    let routerServiceStub: jasmine.SpyObj<RouterService>;
    let dataJobsServiceStub: jasmine.SpyObj<DataJobsService>;
    let errorHandlerServiceStub: jasmine.SpyObj<ErrorHandlerService>;

    let componentModelStub: ComponentModel;
    let component: DataJobsExploreGridComponent;
    let fixture: ComponentFixture<DataJobsExploreGridComponent>;

    const TEST_JOB = {
        jobName: 'job001'
    };

    beforeAll(() => {
        // This hack is needed in order to prevent tests to reload browser.
        // Browser reloading stops Tests execution in the same browser, and need to restart execution from beginning.
        window.onbeforeunload = () => 'Stop browser from reload!';
    });

    beforeEach(() => {
        const activatedRouteStub = () => ({
            queryParams: {
                subscribe: CallFake
            },
            snapshot: null
        });
        const routerStub = () => ({
            url: '/explore/data-jobs'
        });

        componentServiceStub = jasmine.createSpyObj<ComponentService>('componentService', ['init', 'getModel', 'idle', 'update']);
        navigationServiceStub = jasmine.createSpyObj<NavigationService>('navigationService', ['navigate', 'navigateTo', 'navigateBack']);
        dataJobsApiServiceStub = jasmine.createSpyObj<DataJobsApiService>(
            'dataJobsService',
            ['getJobs', 'getJobDetails', 'getJobExecutions']
        );
        dataJobsServiceStub = jasmine.createSpyObj<DataJobsService>('dataJobsService', [
            'loadJobs',
            'notifyForRunningJobExecutionId',
            'notifyForJobExecutions',
            'notifyForTeamImplicitly',
            'getNotifiedForRunningJobExecutionId',
            'getNotifiedForJobExecutions',
            'getNotifiedForTeamImplicitly'
        ]);
        locationStub = jasmine.createSpyObj<Location>('location', ['path', 'go']);
        routerServiceStub = jasmine.createSpyObj<RouterService>('routerService', ['getState', 'get']);
        errorHandlerServiceStub = jasmine.createSpyObj<ErrorHandlerService>('errorHandlerService', [
            'processError',
            'handleError'
        ]);

        dataJobsServiceStub.getNotifiedForJobExecutions.and.returnValue(new Subject());
        dataJobsServiceStub.getNotifiedForTeamImplicitly.and.returnValue(new BehaviorSubject('taurus'));

        componentModelStub = ComponentModel.of(
            ComponentStateImpl.of({}),
            RouterState.empty()
        );
        routerServiceStub.getState.and.returnValue(new Subject());
        routerServiceStub.get.and.returnValue(new Subject());
        componentServiceStub.init.and.returnValue(of(componentModelStub));
        componentServiceStub.getModel.and.returnValue(of(componentModelStub));

        TestBed.configureTestingModule({
            schemas: [NO_ERRORS_SCHEMA],
            declarations: [DataJobsExploreGridComponent],
            providers: [
                {
                    provide: DATA_PIPELINES_CONFIGS,
                    useFactory: () => ({
                        defaultOwnerTeamName: 'all'
                    })
                },
                { provide: RouterService, useValue: routerServiceStub },
                { provide: ComponentService, useValue: componentServiceStub },
                { provide: NavigationService, useValue: navigationServiceStub },
                { provide: ActivatedRoute, useFactory: activatedRouteStub },
                { provide: DataJobsApiService, useValue: dataJobsApiServiceStub },
                { provide: DataJobsService, useValue: dataJobsServiceStub },
                { provide: Location, useValue: locationStub },
                { provide: Router, useFactory: routerStub },
                { provide: ErrorHandlerService, useValue: errorHandlerServiceStub }
            ]
        });

        fixture = TestBed.createComponent(DataJobsExploreGridComponent);
        component = fixture.componentInstance;
        component.teamNameFilter = 'testFilterTeam';
        component.model = componentModelStub;

        dataJobsApiServiceStub.getJobs.and.returnValue(of({
            data: {
                content: [],
                totalItems: 0
            }
        } as ApolloQueryResult<DataJobPage>));
        dataJobsApiServiceStub.getJobDetails.and.returnValue(of(null) as Observable<DataJobDetails>);
        dataJobsApiServiceStub.getJobExecutions.and.returnValue(of({ content: [], totalItems: 0, totalPages: 0 }));

        locationStub.path.and.returnValue('/explore/data-jobs');

        spyOn(SystemEventDispatcher, 'send').and.returnValue(Promise.resolve(true));
    });

    it('can load instance', () => {
        expect(component).toBeTruthy();
    });

    it(`displayMode has default value`, () => {
        expect(component.displayMode).toEqual(DisplayMode.STANDARD);
    });

    it(`loading has default value`, () => {
        expect(component.loading).toBeFalse();
    });

    it(`dataJobs has default value`, () => {
        expect(component.dataJobs).toEqual([]);
    });

    it(`totalJobs has default value`, () => {
        expect(component.totalJobs).toEqual(0);
    });

    describe('urlUpdateStrategy', () => {
        it('should verify the behaviour of _doUrlUpdate when urlUpdateStrategy is default (updateRouter)', () => {
            const navigateToUrlSpy = spyOn(component.urlStateManager, 'navigateToUrl').and.returnValue(Promise.resolve(true));

            // @ts-ignore
            component._doUrlUpdate();

            expect(navigateToUrlSpy).toHaveBeenCalled();
        });

        it('should verify the behaviour of _doUrlUpdate when urlUpdateStrategy is changed (updateLocation)', () => {
            const locationToURLSpy = spyOn(component.urlStateManager, 'locationToURL').and.callFake(CallFake);
            component.urlUpdateStrategy = 'updateLocation';

            // @ts-ignore
            component._doUrlUpdate();

            expect(locationToURLSpy).toHaveBeenCalled();
        });
    });

    describe('urlStateManager', () => {
        it('should verify will invoke default urlStateManager (locally created)', () => {
            // Given
            const setQueryParamSpy = spyOn(component.urlStateManager, 'setQueryParam').and.callFake(CallFake);

            // When
            component.search('search');

            // Then
            expect(setQueryParamSpy).toHaveBeenCalledWith(QUERY_PARAM_SEARCH, 'search');
        });

        it('should verify will invoke external urlStateManager (dependency injected)', () => {
            // Given
            const urlStateManagerStub = new URLStateManager('baseUrl', locationStub);
            const setQueryParamSpy = spyOn(urlStateManagerStub, 'setQueryParam').and.callFake(CallFake);

            // When
            component.urlStateManager = urlStateManagerStub;
            component.search('search');

            // Then
            expect(setQueryParamSpy).toHaveBeenCalledWith(QUERY_PARAM_SEARCH, 'search');
        });

        it('should verify will invoke default urlStateManager (dependency injection is null or undefined)', () => {
            // Given
            const setQueryParamSpy = spyOn(component.urlStateManager, 'setQueryParam').and.callFake(CallFake);

            // When
            component.urlStateManager = null;
            component.search('search test value 1');
            component.urlStateManager = undefined;
            component.search('search test value 2');

            // Then
            expect(setQueryParamSpy.calls.argsFor(0)).toEqual([QUERY_PARAM_SEARCH, 'search test value 1']);
            expect(setQueryParamSpy.calls.argsFor(1)).toEqual([QUERY_PARAM_SEARCH, 'search test value 2']);
        });
    });

    describe('handleStateChange', () => {
        it('makes expected calls', () => {
            const clrDatagridStateInterfaceStub = { filters: [] } as ClrDatagridStateInterface;
            clrDatagridStateInterfaceStub.filters.push({
                property: 'search_prop',
                pattern: '%search%',
                sort: ASC
            });
            component.gridState = clrDatagridStateInterfaceStub;

            // @ts-ignore
            spyOn(component, '_getFilterPattern').and.callThrough();
            // @ts-ignore
            component._doLoadData();
            // @ts-ignore
            expect(component._getFilterPattern).toHaveBeenCalled();
            expect(dataJobsServiceStub.loadJobs).toHaveBeenCalled();
        });
    });

    describe('viewJobDetails', () => {
        it('skips viewJobDetails for undefined job', () => {
            // Given
            const navigateToSpy = spyOn(component, 'navigateTo').and.callFake(CallFake);

            // When
            component.navigateToJobDetails();

            // Then
            expect(component.selectedJob).toBeUndefined();
            expect(navigateToSpy).not.toHaveBeenCalled();
        });

        it('opens viewJobDetails for valid job', () => {
            // Given
            const navigateToSpy = spyOn(component, 'navigateTo').and.returnValue(Promise.resolve(true));
            component.ngOnInit();

            // When
            component.navigateToJobDetails({ jobName: 'job001', config: { team: 'team007' } });

            // Then
            expect(component.selectedJob).toBeDefined();
            expect(navigateToSpy).toHaveBeenCalledWith({
                '$.team': 'team007',
                '$.job': 'job001'
            });
        });
    });

    describe('ngOnInit', () => {
        it('makes expected calls', () => {
            // @ts-ignore
            component.ngOnInit();
            expect(componentServiceStub.init).toHaveBeenCalled();
            expect(componentServiceStub.getModel).toHaveBeenCalled();
        });
    });

    describe('isStandardDisplayMode', () => {
        it('returns expected displayMode with COMPACT', () => {
            component.displayMode = DisplayMode.COMPACT;
            expect(component.isStandardDisplayMode()).toBeFalse();
        });

        it('returns expected displayMode with null', () => {
            component.displayMode = null;
            expect(component.isStandardDisplayMode()).toBeFalse();
        });

        it('returns expected displayMode with STANDARD', () => {
            component.displayMode = DisplayMode.STANDARD;
            expect(component.isStandardDisplayMode()).toBeTrue();
        });
    });

    describe('selectionChanged', () => {
        it('sets expected dataJob', () => {
            component.selectionChanged(TEST_JOB);
            expect(component.selectedJob).toEqual(TEST_JOB);
        });
    });

    describe('search', () => {
        it('makes expected calls', () => {
            spyOn(component, 'loadDataWithState').and.callThrough();
            component.search('searchValue');
            expect(component.searchQueryValue).toBe('searchValue');
            expect(component.loadDataWithState).toHaveBeenCalled();
        });
    });
});
