/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';

import { merge, Observable, of, throwError } from 'rxjs';
import { catchError, map, switchMap, take, tap } from 'rxjs/operators';

import { Actions, createEffect, ofType } from '@ngrx/effects';

import {
    CollectionsUtil,
    ComponentFailed,
    ComponentLoaded,
    ComponentModel,
    ComponentService,
    ComponentState,
    ComponentUpdate,
    extractTaskFromIdentifier,
    generateErrorCode,
    getModel,
    getModelAndTask,
    LOADED,
    processServiceRequestError,
    ServiceHttpErrorCodes,
    StatusType,
    TaurusBaseEffects
} from '@versatiledatakit/shared';

import { ErrorUtil } from '../../shared/utils';

import {
    DataJob,
    DataJobDetails,
    DataJobExecutionFilter,
    DataJobExecutionOrder,
    DataJobPage,
    FILTER_REQ_PARAM,
    JOB_DEPLOYMENT_ID_REQ_PARAM,
    JOB_DETAILS_DATA_KEY,
    JOB_DETAILS_REQ_PARAM,
    JOB_EXECUTIONS_DATA_KEY,
    JOB_NAME_REQ_PARAM,
    JOB_STATE_DATA_KEY,
    JOB_STATE_REQ_PARAM,
    JOB_STATUS_REQ_PARAM,
    JOBS_DATA_KEY,
    ORDER_REQ_PARAM,
    TEAM_NAME_REQ_PARAM
} from '../../model';

import {
    DataJobLoadTasks,
    DataJobsLoadTasks,
    DataJobUpdateTasks,
    TASK_LOAD_JOB_DETAILS,
    TASK_LOAD_JOB_EXECUTIONS,
    TASK_LOAD_JOB_STATE,
    TASK_LOAD_JOBS_STATE,
    TASK_UPDATE_JOB_DESCRIPTION,
    TASK_UPDATE_JOB_STATUS
} from '../tasks';

import { LOAD_JOB_ERROR_CODES, LOAD_JOBS_ERROR_CODES, UPDATE_JOB_DETAILS_ERROR_CODES } from '../error-codes';

import { FETCH_DATA_JOB, FETCH_DATA_JOB_EXECUTIONS, FETCH_DATA_JOBS, UPDATE_DATA_JOB } from '../actions';

import { DataJobsApiService } from '../../services';

/**
 * ** Effect for DataJobs.
 */
@Injectable()
export class DataJobsEffects extends TaurusBaseEffects {
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME = 'DataJobsEffects';

    /**
     * @inheritDoc
     */
    static override readonly PUBLIC_NAME = 'Data-Jobs-Effects';

    /**
     * ** Load DataJobs data.
     */
    loadDataJobs$ = createEffect(() =>
        this.actions$.pipe(
            ofType(FETCH_DATA_JOBS),
            getModel(this.componentService),
            switchMap((model: ComponentModel) => this._loadDataJobs(model))
        )
    );

    loadDataJob$ = createEffect(() =>
        this.actions$.pipe(
            ofType(FETCH_DATA_JOB),
            getModel(this.componentService),
            switchMap((model) =>
                merge(
                    this._executeJobTask(model, TASK_LOAD_JOB_STATE),
                    this._executeJobTask(model, TASK_LOAD_JOB_DETAILS),
                    this._executeJobTask(model, TASK_LOAD_JOB_EXECUTIONS)
                )
            )
        )
    );

    loadDataJobExecutions$ = createEffect(() =>
        this.actions$.pipe(
            ofType(FETCH_DATA_JOB_EXECUTIONS),
            getModel(this.componentService),
            switchMap((model) => this._executeJobTask(model, TASK_LOAD_JOB_EXECUTIONS))
        )
    );

    updateDataJob$ = createEffect(() =>
        this.actions$.pipe(
            ofType(UPDATE_DATA_JOB),
            getModelAndTask(this.componentService),
            switchMap(([model, task]) => this._updateJob(model, task)) // eslint-disable-line rxjs/no-unsafe-switchmap
        )
    );

    /**
     * ** Constructor.
     */
    constructor(
        actions$: Actions,
        componentService: ComponentService,
        private readonly dataJobsApiService: DataJobsApiService
    ) {
        super(actions$, componentService, DataJobsEffects.CLASS_NAME);

        this.registerEffectsErrorCodes();
    }

    /**
     * @inheritDoc
     * @protected
     */
    protected registerEffectsErrorCodes(): void {
        LOAD_JOB_ERROR_CODES[TASK_LOAD_JOB_STATE] = this.dataJobsApiService.errorCodes.getJob;
        LOAD_JOB_ERROR_CODES[TASK_LOAD_JOB_DETAILS] = this.dataJobsApiService.errorCodes.getJobDetails;
        LOAD_JOB_ERROR_CODES[TASK_LOAD_JOB_EXECUTIONS] = this.dataJobsApiService.errorCodes.getJobExecutions;

        LOAD_JOBS_ERROR_CODES[TASK_LOAD_JOBS_STATE] = this.dataJobsApiService.errorCodes.getJobs;

        UPDATE_JOB_DETAILS_ERROR_CODES[TASK_UPDATE_JOB_STATUS] = this.dataJobsApiService.errorCodes.updateDataJobStatus;
        UPDATE_JOB_DETAILS_ERROR_CODES[TASK_UPDATE_JOB_DESCRIPTION] = this.dataJobsApiService.errorCodes.updateDataJob;
    }

    private _loadDataJobs(componentModel: ComponentModel): Observable<ComponentLoaded | ComponentFailed> {
        const componentState = componentModel.getComponentState();
        const task: DataJobsLoadTasks = TASK_LOAD_JOBS_STATE;

        return of(componentModel).pipe(
            switchMap((model) =>
                this.dataJobsApiService
                    .getJobs(componentState.filter.criteria, componentState.search, componentState.page.page, componentState.page.size)
                    .pipe(
                        map((response) =>
                            model
                                .clearTask()
                                .removeErrorCodePatterns(LOAD_JOBS_ERROR_CODES[TASK_LOAD_JOBS_STATE].All)
                                .withData(JOBS_DATA_KEY, response.data)
                                .withTask(task)
                                .withStatusLoaded()
                                .getComponentState()
                        ),
                        map<ComponentState, ComponentLoaded>((state) => ComponentLoaded.of(state)),
                        catchError<ComponentFailed, Observable<ComponentFailed>>((error: unknown) =>
                            this._getLatestModel(model).pipe(
                                map((newModel) =>
                                    ComponentFailed.of(
                                        newModel
                                            .withData(JOBS_DATA_KEY, {
                                                content: [],
                                                totalItems: 0,
                                                totalPages: 0
                                            } as DataJobPage)
                                            .withError(
                                                processServiceRequestError(
                                                    this.objectUUID,
                                                    LOAD_JOBS_ERROR_CODES[TASK_LOAD_JOBS_STATE],
                                                    ErrorUtil.extractError(error as Error)
                                                )
                                            )
                                            .withTask(task)
                                            .withStatusFailed()
                                            .getComponentState()
                                    )
                                )
                            )
                        )
                    )
            )
        );
    }

    private _executeJobTask(model: ComponentModel, task: DataJobLoadTasks): Observable<ComponentLoaded | ComponentFailed> {
        switch (task) {
            case TASK_LOAD_JOB_STATE:
                return this._fetchJobData<DataJob>(
                    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
                    this.dataJobsApiService.getJob.bind(this.dataJobsApiService),
                    LOAD_JOB_ERROR_CODES[TASK_LOAD_JOB_STATE],
                    model,
                    TASK_LOAD_JOB_STATE,
                    JOB_STATE_DATA_KEY
                );
            case TASK_LOAD_JOB_DETAILS:
                return this._fetchJobData(
                    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
                    this.dataJobsApiService.getJobDetails.bind(this.dataJobsApiService),
                    LOAD_JOB_ERROR_CODES[TASK_LOAD_JOB_DETAILS],
                    model,
                    TASK_LOAD_JOB_DETAILS,
                    JOB_DETAILS_DATA_KEY
                );
            case TASK_LOAD_JOB_EXECUTIONS:
                return this._loadDataJobExecutionsGraphQL(model);
            default:
                return throwError(() => new Error('Unknown action task for Data Pipelines.')).pipe(this._handleError(model, null, task));
        }
    }

    private _fetchJobData<T>(
        executor: (param1: string, param2: string) => Observable<T>,
        executorErrorCodes: Readonly<Record<keyof ServiceHttpErrorCodes, string>>,
        componentModel: ComponentModel,
        task: DataJobLoadTasks | string,
        dataKey: string
    ): Observable<ComponentLoaded | ComponentUpdate | ComponentFailed> {
        return of(componentModel).pipe(
            switchMap((model) =>
                executor(
                    componentModel.getComponentState().requestParams.get(TEAM_NAME_REQ_PARAM) as string,
                    componentModel.getComponentState().requestParams.get(JOB_NAME_REQ_PARAM) as string
                ).pipe(
                    switchMap((data) => {
                        let obsoleteStatus: StatusType;

                        return this._getLatestModel(model).pipe(
                            tap((newModel) => (obsoleteStatus = newModel.status)),
                            map((newModel) =>
                                newModel
                                    .removeErrorCodePatterns(executorErrorCodes.All)
                                    .withTask(task)
                                    .withData(dataKey, data)
                                    .withStatusLoaded()
                                    .getComponentState()
                            ),
                            map((state) => (obsoleteStatus === LOADED ? ComponentUpdate.of(state) : ComponentLoaded.of(state)))
                        );
                    }),
                    this._handleError(model, executorErrorCodes, task)
                )
            )
        );
    }

    private _updateJob(model: ComponentModel, taskIdentifier: string): Observable<ComponentUpdate | ComponentFailed> {
        const task = extractTaskFromIdentifier<DataJobUpdateTasks>(taskIdentifier);
        const requestParams = model.getComponentState().requestParams;

        if (task === TASK_UPDATE_JOB_DESCRIPTION) {
            const jobDetails: DataJobDetails = requestParams.get(JOB_DETAILS_REQ_PARAM);

            return this.dataJobsApiService
                .updateDataJob(
                    requestParams.get(TEAM_NAME_REQ_PARAM) as string,
                    requestParams.get(JOB_NAME_REQ_PARAM) as string,
                    jobDetails
                )
                .pipe(
                    map(() =>
                        ComponentLoaded.of(
                            model
                                .removeErrorCodePatterns(UPDATE_JOB_DETAILS_ERROR_CODES[TASK_UPDATE_JOB_DESCRIPTION].All)
                                .withTask(taskIdentifier)
                                .withData(JOB_DETAILS_DATA_KEY, jobDetails)
                                .withStatusLoaded()
                                .getComponentState()
                        )
                    ),
                    this._handleError(model, UPDATE_JOB_DETAILS_ERROR_CODES[TASK_UPDATE_JOB_DESCRIPTION], taskIdentifier)
                );
        }

        if (task === TASK_UPDATE_JOB_STATUS) {
            const jobState: DataJob = model.getComponentState().requestParams.get(JOB_STATE_REQ_PARAM);

            return this.dataJobsApiService
                .updateDataJobStatus(
                    requestParams.get(TEAM_NAME_REQ_PARAM) as string,
                    requestParams.get(JOB_NAME_REQ_PARAM) as string,
                    requestParams.get(JOB_DEPLOYMENT_ID_REQ_PARAM) as string,
                    requestParams.get(JOB_STATUS_REQ_PARAM) as boolean
                )
                .pipe(
                    map(() =>
                        ComponentLoaded.of(
                            model
                                .removeErrorCodePatterns(UPDATE_JOB_DETAILS_ERROR_CODES[TASK_UPDATE_JOB_STATUS].All)
                                .withTask(taskIdentifier)
                                .withData(JOB_STATE_DATA_KEY, jobState)
                                .withStatusLoaded()
                                .getComponentState()
                        )
                    ),
                    this._handleError(model, UPDATE_JOB_DETAILS_ERROR_CODES[TASK_UPDATE_JOB_STATUS], taskIdentifier)
                );
        }

        const error = new Error('Unsupported action task for Data Pipelines, update Data Job.');

        console.error(error);

        return of(
            ComponentFailed.of(
                model
                    .withTask(taskIdentifier)
                    .withError({
                        objectUUID: this.objectUUID,
                        code: generateErrorCode(
                            DataJobsEffects.CLASS_NAME,
                            DataJobsEffects.PUBLIC_NAME,
                            '_updateJob',
                            'UnsupportedActionTask'
                        ),
                        error
                    })
                    .withStatusFailed()
                    .getComponentState()
            )
        );
    }

    private _loadDataJobExecutionsGraphQL(componentModel: ComponentModel): Observable<ComponentLoaded> {
        const componentState = componentModel.getComponentState();
        const requestParams = componentState.requestParams;

        return of(componentModel).pipe(
            switchMap((model) =>
                this.dataJobsApiService
                    .getJobExecutions(
                        requestParams.get(TEAM_NAME_REQ_PARAM) as string,
                        requestParams.get(JOB_NAME_REQ_PARAM) as string,
                        true,
                        requestParams.get(FILTER_REQ_PARAM) as DataJobExecutionFilter,
                        requestParams.get(ORDER_REQ_PARAM) as DataJobExecutionOrder
                    )
                    .pipe(
                        switchMap((response) => {
                            let obsoleteStatus: StatusType;

                            return this._getLatestModel(model).pipe(
                                tap((newModel) => (obsoleteStatus = newModel.status)),
                                map((newModel) =>
                                    newModel
                                        .removeErrorCodePatterns(LOAD_JOB_ERROR_CODES[TASK_LOAD_JOB_EXECUTIONS].All)
                                        .withTask(TASK_LOAD_JOB_EXECUTIONS)
                                        .withData(JOB_EXECUTIONS_DATA_KEY, response.content)
                                        .withStatusLoaded()
                                        .getComponentState()
                                ),
                                map((state) => (obsoleteStatus === LOADED ? ComponentUpdate.of(state) : ComponentLoaded.of(state)))
                            );
                        }),
                        this._handleError(model, LOAD_JOB_ERROR_CODES[TASK_LOAD_JOB_EXECUTIONS], TASK_LOAD_JOB_EXECUTIONS)
                    )
            )
        );
    }

    private _getLatestModel(componentModel: ComponentModel): Observable<ComponentModel> {
        const componentState = componentModel.getComponentState();

        return this.componentService.getModel(componentState.id, componentState.routePathSegments, ['*']).pipe(take(1));
    }

    private _handleError(
        obsoleteModel: ComponentModel,
        executorErrorCodes: Readonly<Record<keyof ServiceHttpErrorCodes, string>>,
        task: DataJobLoadTasks | string
    ) {
        return catchError<ComponentLoaded | ComponentUpdate, Observable<ComponentFailed>>((error: unknown) => {
            return this._getLatestModel(obsoleteModel).pipe(
                map((newModel) =>
                    newModel
                        .withTask(task)
                        .withError(
                            CollectionsUtil.isLiteralObject(executorErrorCodes)
                                ? processServiceRequestError(this.objectUUID, executorErrorCodes, ErrorUtil.extractError(error as Error))
                                : {
                                      objectUUID: this.objectUUID,
                                      code: generateErrorCode(
                                          DataJobsEffects.CLASS_NAME,
                                          DataJobsEffects.PUBLIC_NAME,
                                          '_handleError',
                                          'GenericError'
                                      ),
                                      error: error as Error
                                  }
                        )
                        .withStatusFailed()
                        .getComponentState()
                ),
                map<ComponentState, ComponentFailed>((state) => ComponentFailed.of(state))
            );
        });
    }
}
