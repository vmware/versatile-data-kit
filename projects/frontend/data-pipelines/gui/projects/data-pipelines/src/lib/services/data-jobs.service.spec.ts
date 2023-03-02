/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { Observable } from 'rxjs';

import {
    ComponentModel,
    ComponentService,
    ComponentStateImpl,
    RouterState,
    RouteState,
} from '@versatiledatakit/shared';

import {
    FETCH_DATA_JOB,
    FETCH_DATA_JOB_EXECUTIONS,
    FETCH_DATA_JOBS,
    UPDATE_DATA_JOB,
} from '../state/actions';
import {
    TASK_LOAD_JOB_EXECUTIONS,
    TASK_UPDATE_JOB_DESCRIPTION,
} from '../state/tasks';

import { DataJobsService, DataJobsServiceImpl } from './data-jobs.service';

describe('DataJobsService -> DataJobsServiceImpl', () => {
    let componentServiceStub: jasmine.SpyObj<ComponentService>;

    let service: DataJobsService;

    beforeEach(() => {
        componentServiceStub = jasmine.createSpyObj<ComponentService>(
            'componentService',
            ['load', 'dispatchAction']
        );

        TestBed.configureTestingModule({
            providers: [
                { provide: ComponentService, useValue: componentServiceStub },
                { provide: DataJobsService, useClass: DataJobsServiceImpl },
            ],
        });

        service = TestBed.inject(DataJobsService);
    });

    it('should verify instance is created', () => {
        // Then
        expect(service).toBeDefined();
    });

    describe('Methods::', () => {
        describe('|loadJob|', () => {
            it('should verify will invoke expected method', () => {
                // Given
                const model = ComponentModel.of(
                    ComponentStateImpl.of({
                        id: 'test-component',
                    }),
                    RouterState.of(RouteState.empty(), 1)
                );

                // When
                service.loadJob(model);

                // Then
                expect(componentServiceStub.load).toHaveBeenCalledWith(
                    model.getComponentState()
                );
                expect(
                    componentServiceStub.dispatchAction
                ).toHaveBeenCalledWith(
                    FETCH_DATA_JOB,
                    model.getComponentState()
                );
            });
        });

        describe('|loadJobs|', () => {
            it('should verify will invoke expected method', () => {
                // Given
                const model = ComponentModel.of(
                    ComponentStateImpl.of({
                        id: 'test-component',
                    }),
                    RouterState.of(RouteState.empty(), 1)
                );

                // When
                service.loadJobs(model);

                // Then
                expect(componentServiceStub.load).toHaveBeenCalledWith(
                    model.getComponentState()
                );
                expect(
                    componentServiceStub.dispatchAction
                ).toHaveBeenCalledWith(
                    FETCH_DATA_JOBS,
                    model.getComponentState()
                );
            });
        });

        describe('|loadJobExecutions|', () => {
            it('should verify will invoke expected method', () => {
                // Given
                const model = ComponentModel.of(
                    ComponentStateImpl.of({
                        id: 'test-component',
                    }),
                    RouterState.of(RouteState.empty(), 1)
                );

                // When
                service.loadJobExecutions(model);

                // Then
                expect(componentServiceStub.load).toHaveBeenCalledWith(
                    model.getComponentState()
                );
                expect(
                    componentServiceStub.dispatchAction
                ).toHaveBeenCalledWith(
                    FETCH_DATA_JOB_EXECUTIONS,
                    model.getComponentState(),
                    TASK_LOAD_JOB_EXECUTIONS
                );
            });
        });

        describe('|updateJob|', () => {
            it('should verify will invoke expected method', () => {
                // Given
                const model = ComponentModel.of(
                    ComponentStateImpl.of({
                        id: 'test-component',
                    }),
                    RouterState.of(RouteState.empty(), 1)
                );

                // When
                service.updateJob(model, TASK_UPDATE_JOB_DESCRIPTION);

                // Then
                expect(componentServiceStub.load).toHaveBeenCalledWith(
                    model.getComponentState()
                );
                expect(
                    componentServiceStub.dispatchAction
                ).toHaveBeenCalledWith(
                    UPDATE_DATA_JOB,
                    model.getComponentState(),
                    TASK_UPDATE_JOB_DESCRIPTION
                );
            });
        });

        describe('|getNotifiedForRunningJobExecutionId|', () => {
            it('should verify will return Observable', () => {
                // Given
                // eslint-disable-next-line @typescript-eslint/dot-notation
                const asObservableSpy = spyOn(
                    (service as DataJobsServiceImpl)['_runningJobExecutionId'],
                    'asObservable'
                ).and.callThrough();

                // When
                const observable =
                    service.getNotifiedForRunningJobExecutionId();

                // Then
                expect(observable).toBeInstanceOf(Observable);
                expect(asObservableSpy).toHaveBeenCalled();
            });
        });

        describe('|notifyForRunningJobExecutionId|', () => {
            it('should verify will notify correct Subject', () => {
                // Given
                // eslint-disable-next-line @typescript-eslint/dot-notation
                const nextSpy = spyOn(
                    (service as DataJobsServiceImpl)['_runningJobExecutionId'],
                    'next'
                ).and.callThrough();

                // When
                service.notifyForRunningJobExecutionId('xy');

                // Then
                expect(nextSpy).toHaveBeenCalledWith('xy');
            });
        });

        describe('|getNotifiedForJobExecutions|', () => {
            it('should verify will return Observable', () => {
                // Given
                // eslint-disable-next-line @typescript-eslint/dot-notation
                const asObservableSpy = spyOn(
                    (service as DataJobsServiceImpl)['_jobExecutions'],
                    'asObservable'
                ).and.callThrough();

                // When
                const observable = service.getNotifiedForJobExecutions();

                // Then
                expect(observable).toBeInstanceOf(Observable);
                expect(asObservableSpy).toHaveBeenCalled();
            });
        });

        describe('|notifyForJobExecutions|', () => {
            it('should verify will notify correct Subject', () => {
                // Given
                // eslint-disable-next-line @typescript-eslint/dot-notation
                const nextSpy = spyOn(
                    (service as DataJobsServiceImpl)['_jobExecutions'],
                    'next'
                ).and.callThrough();

                // When
                service.notifyForJobExecutions([null]);

                // Then
                expect(nextSpy).toHaveBeenCalledWith([null]);
            });
        });

        describe('|getNotifiedForTeamImplicitly|', () => {
            it('should verify will return Observable', () => {
                // Given
                // eslint-disable-next-line @typescript-eslint/dot-notation
                const asObservableSpy = spyOn(
                    (service as DataJobsServiceImpl)['_implicitTeam'],
                    'asObservable'
                ).and.callThrough();

                // When
                const observable = service.getNotifiedForTeamImplicitly();

                // Then
                expect(observable).toBeInstanceOf(Observable);
                expect(asObservableSpy).toHaveBeenCalled();
            });
        });

        describe('|notifyForTeamImplicitly|', () => {
            it('should verify will notify correct BehaviorSubject', () => {
                // Given
                // eslint-disable-next-line @typescript-eslint/dot-notation
                const nextSpy = spyOn(
                    (service as DataJobsServiceImpl)['_implicitTeam'],
                    'next'
                ).and.callThrough();

                // When
                service.notifyForTeamImplicitly('teamZero');

                // Then
                expect(nextSpy).toHaveBeenCalledWith('teamZero');
            });
        });
    });
});
