/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/naming-convention */

import { TestBed, waitForAsync } from '@angular/core/testing';

import { Observable, throwError } from 'rxjs';

import { marbles } from 'rxjs-marbles/jasmine';

import { provideMockActions } from '@ngrx/effects/testing';

import { ApolloQueryResult } from '@apollo/client/core';

import {
    CollectionsUtil,
    ComponentFailed,
    ComponentLoaded,
    ComponentModel,
    ComponentService,
    ComponentStateImpl,
    ComponentUpdate,
    ErrorRecord,
    generateErrorCode,
    generateErrorCodes,
    GenericAction,
    LOADED,
    LOADING,
    RouterState,
    RouteState,
    StatusType,
} from '@versatiledatakit/shared';

import { DataJobsApiService } from '../../services';

import {
    DataJob,
    DataJobDetails,
    DataJobExecutionsPage,
    DataJobPage,
    JOB_DEPLOYMENT_ID_REQ_PARAM,
    JOB_DETAILS_DATA_KEY,
    JOB_EXECUTIONS_DATA_KEY,
    JOB_NAME_REQ_PARAM,
    JOB_STATE_DATA_KEY,
    JOBS_DATA_KEY,
    TEAM_NAME_REQ_PARAM,
} from '../../model';

import {
    FETCH_DATA_JOB,
    FETCH_DATA_JOB_EXECUTIONS,
    FETCH_DATA_JOBS,
    UPDATE_DATA_JOB,
} from '../actions';

import { DataJobsEffects } from './data-jobs.effects';
import {
    TASK_LOAD_JOB_DETAILS,
    TASK_LOAD_JOB_EXECUTIONS,
    TASK_LOAD_JOB_STATE,
    TASK_LOAD_JOBS_STATE,
    TASK_UPDATE_JOB_DESCRIPTION,
    TASK_UPDATE_JOB_STATUS,
} from '../tasks';

describe('DataJobsEffects', () => {
    let effects: DataJobsEffects;

    let actions$: Observable<any>;

    let dataJobsApiServiceStub: jasmine.SpyObj<DataJobsApiService>;
    let componentServiceStub: jasmine.SpyObj<ComponentService>;

    beforeEach(waitForAsync(() => {
        dataJobsApiServiceStub = jasmine.createSpyObj<DataJobsApiService>(
            'dataJobsApiService',
            [
                'getJobs',
                'getJob',
                'getJobDetails',
                'getJobExecutions',
                'updateDataJob',
                'updateDataJobStatus',
            ],
        );
        componentServiceStub = jasmine.createSpyObj<ComponentService>(
            'componentService',
            ['getModel'],
        );

        generateErrorCodes<DataJobsApiService>(dataJobsApiServiceStub, [
            'getJob',
            'getJobDetails',
            'getJobExecutions',
            'getJobs',
            'updateDataJobStatus',
            'updateDataJob',
        ]);

        TestBed.configureTestingModule({
            providers: [
                {
                    provide: DataJobsApiService,
                    useValue: dataJobsApiServiceStub,
                },
                {
                    provide: ComponentService,
                    useValue: componentServiceStub,
                },
                provideMockActions(() => actions$),
                DataJobsEffects,
            ],
        });

        effects = TestBed.inject(DataJobsEffects);
    }));

    describe('Effects::', () => {
        describe('|loadDataJobs$|', () => {
            it(
                'should verify will load data-jobs',
                marbles((m) => {
                    // Given
                    const dateNow = Date.now();
                    spyOn(CollectionsUtil, 'dateNow').and.returnValue(dateNow);
                    const error = new Error('Something bad happened');
                    const errorRecord: ErrorRecord = {
                        code: dataJobsApiServiceStub.errorCodes.getJobs.Unknown,
                        error,
                        objectUUID: effects.objectUUID,
                    };

                    actions$ = m.cold('-a---------b', {
                        a: GenericAction.of(
                            FETCH_DATA_JOBS,
                            createModel().getComponentState(),
                        ),
                        b: GenericAction.of(
                            FETCH_DATA_JOBS,
                            createModel(null, 4).getComponentState(),
                        ),
                    });

                    let cntComponentServiceStub = 0;
                    componentServiceStub.getModel.and.callFake(() => {
                        cntComponentServiceStub++;

                        if (cntComponentServiceStub === 1) {
                            return m.cold('--a', { a: createModel() });
                        }

                        return m.cold('--a', { a: createModel(null, 4) });
                    });

                    const result = {
                        data: {
                            content: [
                                { jobName: 'job1' },
                                { jobName: 'job2' },
                                { jobName: 'job3' },
                            ],
                            totalPages: 0,
                            totalItems: 0,
                        },
                    } as ApolloQueryResult<DataJobPage>;

                    let cntDataJobsApiServiceStub = 0;
                    dataJobsApiServiceStub.getJobs.and.callFake(() => {
                        cntDataJobsApiServiceStub++;

                        if (cntDataJobsApiServiceStub === 1) {
                            return m.cold('-----a', {
                                a: result,
                            });
                        }

                        return throwError(
                            () => new Error('Something bad happened'),
                        );
                    });

                    const expected$ = m.cold('--------a------b', {
                        a: ComponentLoaded.of(
                            createModel()
                                .withData(JOBS_DATA_KEY, result.data)
                                .withTask(TASK_LOAD_JOBS_STATE)
                                .withStatusLoaded()
                                .getComponentState(),
                        ),
                        b: ComponentFailed.of(
                            createModel(null, 4)
                                .withData(JOBS_DATA_KEY, {
                                    content: [],
                                    totalItems: 0,
                                    totalPages: 0,
                                } as DataJobPage)
                                .withError(errorRecord)
                                .withTask(TASK_LOAD_JOBS_STATE)
                                .withStatusFailed()
                                .getComponentState(),
                        ),
                    });

                    // When
                    const response$ = effects.loadDataJobs$;

                    // Then
                    m.expect(response$).toBeObservable(expected$);
                }),
            );
        });

        describe('|loadDataJob$|', () => {
            it(
                'should verify will load data-job',
                marbles((m) => {
                    // Given
                    actions$ = m.cold('-a----------', {
                        a: GenericAction.of(
                            FETCH_DATA_JOB,
                            createModel().getComponentState(),
                        ),
                    });

                    let cntComponentServiceStub = 0;
                    componentServiceStub.getModel.and.callFake(() => {
                        cntComponentServiceStub++;

                        switch (cntComponentServiceStub) {
                            case 1:
                                return m.cold('--a', { a: createModel() });
                            case 2:
                                return m.cold('---a', { a: createModel() });
                            case 3:
                                return m.cold('---a', {
                                    a: createModel(
                                        new Map<string, any>([
                                            getJobStateTuple(),
                                        ]),
                                        1,
                                        LOADED,
                                    ),
                                });
                            case 4:
                                return m.cold('---a', {
                                    a: createModel(
                                        new Map<string, any>([
                                            getJobStateTuple(),
                                            getDataJobDetailsTuple(),
                                        ]),
                                        1,
                                        LOADED,
                                    ),
                                });
                            default:
                                return m.cold('---a', {
                                    a: createModel(
                                        new Map<string, any>([
                                            getJobStateTuple(),
                                            getDataJobDetailsTuple(),
                                            [
                                                getExecutionsTuples()[0],
                                                getExecutionsTuples()[1]
                                                    .content,
                                            ],
                                        ]),
                                        1,
                                        LOADED,
                                    ),
                                });
                        }
                    });

                    dataJobsApiServiceStub.getJob.and.returnValue(
                        m.cold('--a', {
                            a: getJobStateTuple()[1],
                        }),
                    );

                    dataJobsApiServiceStub.getJobDetails.and.returnValue(
                        m.cold('----a', {
                            a: getDataJobDetailsTuple()[1],
                        }),
                    );

                    dataJobsApiServiceStub.getJobExecutions.and.returnValue(
                        m.cold('------a', {
                            a: getExecutionsTuples()[1],
                        }),
                    );

                    const expected$ = m.cold('--------a-b-c', {
                        a: ComponentLoaded.of(
                            createModel()
                                .clearError()
                                .withTask(TASK_LOAD_JOB_STATE)
                                .withData(
                                    JOB_STATE_DATA_KEY,
                                    getJobStateTuple()[1],
                                )
                                .withStatusLoaded()
                                .getComponentState(),
                        ),
                        b: ComponentUpdate.of(
                            createModel()
                                .clearError()
                                .withTask(TASK_LOAD_JOB_DETAILS)
                                .withData(
                                    JOB_STATE_DATA_KEY,
                                    getJobStateTuple()[1],
                                )
                                .withData(
                                    JOB_DETAILS_DATA_KEY,
                                    getDataJobDetailsTuple()[1],
                                )
                                .withStatusLoaded()
                                .getComponentState(),
                        ),
                        c: ComponentUpdate.of(
                            createModel()
                                .clearError()
                                .withTask(TASK_LOAD_JOB_EXECUTIONS)
                                .withData(
                                    JOB_STATE_DATA_KEY,
                                    getJobStateTuple()[1],
                                )
                                .withData(
                                    JOB_DETAILS_DATA_KEY,
                                    getDataJobDetailsTuple()[1],
                                )
                                .withData(
                                    JOB_EXECUTIONS_DATA_KEY,
                                    getExecutionsTuples()[1].content,
                                )
                                .withStatusLoaded()
                                .getComponentState(),
                        ),
                    });

                    // When
                    const response$ = effects.loadDataJob$;

                    // Then
                    m.expect(response$).toBeObservable(expected$);
                }),
            );
        });

        describe('|loadDataJobExecutions$|', () => {
            it(
                'should verify will load data-job executions',
                marbles((m) => {
                    // Given
                    const genericAction = GenericAction.of(
                        FETCH_DATA_JOB_EXECUTIONS,
                        createModel().getComponentState(),
                    );
                    actions$ = m.cold('-a----------', {
                        a: genericAction,
                    });

                    let cntComponentServiceStub = 0;
                    componentServiceStub.getModel.and.callFake(() => {
                        cntComponentServiceStub++;

                        switch (cntComponentServiceStub) {
                            case 1:
                                return m.cold('--a', { a: createModel() });
                            case 2:
                                return m.cold('---a', { a: createModel() });
                            default:
                                return m.cold('---a', {
                                    a: createModel(
                                        new Map<string, any>([
                                            [
                                                getExecutionsTuples()[0],
                                                getExecutionsTuples()[1]
                                                    .content,
                                            ],
                                        ]),
                                        1,
                                        LOADED,
                                    ),
                                });
                        }
                    });

                    dataJobsApiServiceStub.getJobExecutions.and.returnValue(
                        m.cold('--a', {
                            a: getExecutionsTuples()[1],
                        }),
                    );

                    const expected$ = m.cold('--------a', {
                        a: ComponentLoaded.of(
                            createModel()
                                .clearError()
                                .withTask(TASK_LOAD_JOB_EXECUTIONS)
                                .withData(
                                    JOB_EXECUTIONS_DATA_KEY,
                                    getExecutionsTuples()[1].content,
                                )
                                .withStatusLoaded()
                                .getComponentState(),
                        ),
                    });

                    // When
                    const response$ = effects.loadDataJobExecutions$;

                    // Then
                    m.expect(response$).toBeObservable(expected$);
                }),
            );
        });

        describe('|updateDataJob$|', () => {
            it(
                'should verify will update data-job description',
                marbles((m) => {
                    // Given
                    const genericAction1 = GenericAction.of(
                        UPDATE_DATA_JOB,
                        createModel(undefined, 1, LOADING).getComponentState(),
                        TASK_UPDATE_JOB_DESCRIPTION,
                    );
                    actions$ = m.cold('-a----------', {
                        a: genericAction1,
                    });

                    componentServiceStub.getModel.and.callFake(() =>
                        m.cold('---a', {
                            a: createModel(undefined, 1, LOADING),
                        }),
                    );

                    dataJobsApiServiceStub.updateDataJob.and.returnValue(
                        m.cold('-----a', {
                            a: getDataJobDetailsTuple()[1],
                        }),
                    );

                    const expected$ = m.cold('---------a-', {
                        a: ComponentLoaded.of(
                            createModel(undefined, 1, LOADING)
                                .clearError()
                                .withTask(genericAction1.task)
                                .withData(JOB_DETAILS_DATA_KEY, undefined)
                                .withStatusLoaded()
                                .getComponentState(),
                        ),
                    });

                    // When
                    const response$ = effects.updateDataJob$;

                    // Then
                    m.expect(response$).toBeObservable(expected$);
                }),
            );

            it(
                'should verify will update data-job status',
                marbles((m) => {
                    // Given
                    const genericAction1 = GenericAction.of(
                        UPDATE_DATA_JOB,
                        createModel(undefined, 1, LOADING).getComponentState(),
                        TASK_UPDATE_JOB_STATUS,
                    );
                    actions$ = m.cold('-a----------', {
                        a: genericAction1,
                    });

                    componentServiceStub.getModel.and.callFake(() =>
                        m.cold('---a', {
                            a: createModel(undefined, 1, LOADING),
                        }),
                    );

                    dataJobsApiServiceStub.updateDataJobStatus.and.returnValue(
                        m.cold('-----a', {
                            a: { enabled: true },
                        }),
                    );

                    const expected$ = m.cold('---------a-', {
                        a: ComponentLoaded.of(
                            createModel(undefined, 1, LOADING)
                                .clearError()
                                .withTask(genericAction1.task)
                                .withData(JOB_STATE_DATA_KEY, undefined)
                                .withStatusLoaded()
                                .getComponentState(),
                        ),
                    });

                    // When
                    const response$ = effects.updateDataJob$;

                    // Then
                    m.expect(response$).toBeObservable(expected$);
                }),
            );

            it(
                'should verify will fail',
                marbles((m) => {
                    // Given
                    const dateNow = Date.now();
                    spyOn(CollectionsUtil, 'dateNow').and.returnValue(dateNow);
                    const error = new Error(
                        'Unsupported action task for Data Pipelines, update Data Job.',
                    );
                    const errorRecord: ErrorRecord = {
                        code: generateErrorCode(
                            DataJobsEffects.CLASS_NAME,
                            DataJobsEffects.PUBLIC_NAME,
                            '_updateJob',
                            'UnsupportedActionTask',
                        ),
                        error,
                        objectUUID: effects.objectUUID,
                    };
                    const genericAction1 = GenericAction.of(
                        UPDATE_DATA_JOB,
                        createModel(undefined, 1, LOADING).getComponentState(),
                        TASK_LOAD_JOB_STATE,
                    );
                    actions$ = m.cold('-a----------', {
                        a: genericAction1,
                    });

                    componentServiceStub.getModel.and.callFake(() =>
                        m.cold('---a', {
                            a: createModel(),
                        }),
                    );

                    const expected$ = m.cold('----a-', {
                        a: ComponentFailed.of(
                            createModel()
                                .withTask(genericAction1.task)
                                .withError(errorRecord)
                                .withStatusFailed()
                                .getComponentState(),
                        ),
                    });

                    // When
                    const response$ = effects.updateDataJob$;

                    // Then
                    m.expect(response$).toBeObservable(expected$);
                }),
            );
        });
    });
});

const createModel = (
    data?: Map<string, any>,
    navigationId = 1,
    status: StatusType = LOADING,
    requestParams: Array<[string, any]> = [],
) =>
    ComponentModel.of(
        ComponentStateImpl.of({
            id: 'testComponent',
            status,
            data,
            requestParams: new Map<string, any>([
                [TEAM_NAME_REQ_PARAM, 'aTeam'],
                [JOB_NAME_REQ_PARAM, 'aJob'],
                [JOB_DEPLOYMENT_ID_REQ_PARAM, 'aJobDeploymentId'],
                ...requestParams,
            ]),
            navigationId,
        }),
        RouterState.of(RouteState.empty(), navigationId),
    );

const getJobStateTuple = () =>
    [
        JOB_STATE_DATA_KEY,
        {
            jobName: 'aJob',
            deployments: [],
            config: {
                schedule: {
                    scheduleCron: '5 5 5 5 *',
                },
                description: 'aDesc',
                team: 'aTeam',
                logsUrl: 'http://url',
                sourceUrl: 'http://urlsource',
            },
        },
    ] as [string, DataJob];

const getDataJobDetailsTuple = () =>
    [
        JOB_DETAILS_DATA_KEY,
        {
            job_name: 'aJob',
            team: 'aTeam',
            description: 'aDesc',
            config: {
                schedule: {
                    schedule_cron: '5 5 5 5 *',
                },
                contacts: {
                    notified_on_job_success: [],
                    notified_on_job_failure_user_error: [],
                    notified_on_job_failure_platform_error: [],
                    notified_on_job_deploy: [],
                },
            },
        },
    ] as [string, DataJobDetails];

const getExecutionsTuples = () =>
    [
        JOB_EXECUTIONS_DATA_KEY,
        {
            content: [
                { jobName: 'aJob', logsUrl: 'http://a1', id: 'a1' },
                { jobName: 'aJob', logsUrl: 'http://a2', id: 'a2' },
                { jobName: 'aJob', logsUrl: 'http://a3', id: 'a3' },
                { jobName: 'aJob', logsUrl: 'http://a4', id: 'a4' },
            ],
            totalPages: 1,
            totalItems: 4,
        },
    ] as [string, DataJobExecutionsPage];
