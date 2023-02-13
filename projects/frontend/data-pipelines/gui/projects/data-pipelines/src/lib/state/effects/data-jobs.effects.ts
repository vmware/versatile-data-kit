/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable ngrx/avoid-cyclic-effects */

import { Injectable } from '@angular/core';

import { merge, Observable, of, throwError } from 'rxjs';
import { catchError, map, switchMap, take, tap } from 'rxjs/operators';

import { Actions, createEffect, ofType } from '@ngrx/effects';

import {
    ComponentFailed,
    ComponentLoaded,
    ComponentModel,
    ComponentService,
    ComponentState,
    ComponentUpdate,
    extractTaskFromIdentifier,
    getModel,
    getModelAndTask,
    handleActionError,
    LOADED,
    StatusType
} from '@vdk/shared';

import { DataJobsApiService } from '../../services';

import {
    DataJob,
    DataJobDetails,
    DataJobExecutionFilter,
    DataJobExecutionOrder,
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

import { FETCH_DATA_JOB, FETCH_DATA_JOB_EXECUTIONS, FETCH_DATA_JOBS, UPDATE_DATA_JOB } from '../actions';
import {
    DataJobLoadTasks,
    DataJobUpdateTasks,
    TASK_LOAD_JOB_DETAILS,
    TASK_LOAD_JOB_EXECUTIONS,
    TASK_LOAD_JOB_STATE,
    TASK_UPDATE_JOB_DESCRIPTION,
    TASK_UPDATE_JOB_STATUS
} from '../tasks';

/**
 * ** Effect for DataJobs.
 */
@Injectable()
export class DataJobsEffects {
    /**
     * ** Load DataJobs data.
     */
    loadDataJobs$ = createEffect(() => this.actions$.pipe(
        ofType(FETCH_DATA_JOBS),
        getModel(this.componentService),
        switchMap((model: ComponentModel) => this._loadDataJobs(model))
    ));

    loadDataJob$ = createEffect(() => this.actions$.pipe(
        ofType(FETCH_DATA_JOB),
        getModel(this.componentService),
        switchMap((model) =>
            merge(
                this._executeJobTask(model, TASK_LOAD_JOB_STATE),
                this._executeJobTask(model, TASK_LOAD_JOB_DETAILS),
                this._executeJobTask(model, TASK_LOAD_JOB_EXECUTIONS)
            )
        )
    ));

    loadDataJobExecutions$ = createEffect(() => this.actions$.pipe(
        ofType(FETCH_DATA_JOB_EXECUTIONS),
        getModelAndTask(this.componentService),
        switchMap(([model, task]) => this._loadDataJobExecutionsGraphQL(model, task))
    ));

    updateDataJob$ = createEffect(() => this.actions$.pipe(
        ofType(UPDATE_DATA_JOB),
        getModelAndTask(this.componentService),
        switchMap(([model, task]) => this._updateJob(model, task)) // eslint-disable-line rxjs/no-unsafe-switchmap
    ));

    /**
     * ** Constructor.
     */
    constructor(private readonly actions$: Actions,
                private readonly dataJobsApiService: DataJobsApiService,
                private readonly componentService: ComponentService) {
    }

    private _loadDataJobs(componentModel: ComponentModel): Observable<ComponentLoaded | ComponentFailed> {
        const componentState = componentModel.getComponentState();

        return of(componentModel).pipe(
            switchMap((model) =>
                this.dataJobsApiService.getJobs(
                    componentState.filter.criteria,
                    componentState.search,
                    componentState.page.page,
                    componentState.page.size
                ).pipe(
                    map((response) =>
                        model
                            .clearTask()
                            .clearError()
                            .withData(JOBS_DATA_KEY, response.data)
                            .withStatusLoaded()
                            .getComponentState()
                    ),
                    map((state) => ComponentLoaded.of(state)),
                    handleActionError(model)
                )
            )
        );
    }

    private _executeJobTask(model: ComponentModel,
                            task: DataJobLoadTasks): Observable<ComponentLoaded | ComponentFailed> {

        switch (task) {
            case TASK_LOAD_JOB_STATE:
                return this._fetchJobData<DataJob>(
                    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
                    this.dataJobsApiService.getJob.bind(this.dataJobsApiService),
                    model,
                    TASK_LOAD_JOB_STATE,
                    JOB_STATE_DATA_KEY
                );
            case TASK_LOAD_JOB_DETAILS:
                return this._fetchJobData(
                    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
                    this.dataJobsApiService.getJobDetails.bind(this.dataJobsApiService),
                    model,
                    TASK_LOAD_JOB_DETAILS,
                    JOB_DETAILS_DATA_KEY
                );
            case TASK_LOAD_JOB_EXECUTIONS:
                return this._loadDataJobExecutionsGraphQL(model, TASK_LOAD_JOB_EXECUTIONS);
            default:
                return throwError(() => new Error('Unknown action task for Data Pipelines.')).pipe(
                    this._handleError(model, task)
                );
        }
    }

    private _fetchJobData<T>(executor: ((param1: string, param2: string) => Observable<T>),
                             componentModel: ComponentModel,
                             task: DataJobLoadTasks | string,
                             dataKey: string): Observable<ComponentLoaded | ComponentUpdate | ComponentFailed> {

        return of(componentModel).pipe(
            switchMap((model) =>
                executor(
                    componentModel.getComponentState().requestParams.get(TEAM_NAME_REQ_PARAM) as string,
                    componentModel.getComponentState().requestParams.get(JOB_NAME_REQ_PARAM) as string
                ).pipe(
                    switchMap((data) => {
                        let obsoleteStatus: StatusType;

                        return this._getLatestModel(model).pipe(
                            tap((newModel) => obsoleteStatus = newModel.status),
                            map((newModel) =>
                                newModel
                                    .clearError()
                                    .withTask(task)
                                    .withData(dataKey, data)
                                    .withStatusLoaded()
                                    .getComponentState()
                            ),
                            map((state) =>
                                obsoleteStatus === LOADED
                                    ? ComponentUpdate.of(state)
                                    : ComponentLoaded.of(state)
                            )
                        );
                    }),
                    this._handleError(model, task)
                )
            )
        );
    }

    private _updateJob(model: ComponentModel,
                       taskIdentifier: string): Observable<ComponentUpdate | ComponentFailed> {

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
                           map(() => ComponentLoaded.of(
                                   model
                                       .clearError()
                                       .withTask(taskIdentifier)
                                       .withData(JOB_DETAILS_DATA_KEY, jobDetails)
                                       .withStatusLoaded()
                                       .getComponentState()
                               )
                           ),
                           this._handleError(model, taskIdentifier)
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
                           map(() => ComponentLoaded.of(
                                   model
                                       .clearError()
                                       .withTask(taskIdentifier)
                                       .withData(JOB_STATE_DATA_KEY, jobState)
                                       .withStatusLoaded()
                                       .getComponentState()
                               )
                           ),
                           this._handleError(model, taskIdentifier)
                       );
        }

        const error = new Error('Unsupported action task for Data Pipelines, update Data Job.');

        console.error(error);

        return of(
            ComponentFailed.of(
                model
                    .withTask(taskIdentifier)
                    .withError(error)
                    .withStatusFailed()
                    .getComponentState()
            )
        );
    }

    private _loadDataJobExecutionsGraphQL(componentModel: ComponentModel,
                                          task: DataJobLoadTasks | DataJobUpdateTasks | string = null): Observable<ComponentLoaded> {

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
                                tap((newModel) => obsoleteStatus = newModel.status),
                                map((newModel) =>
                                    newModel
                                        .clearError()
                                        .withTask(task)
                                        .withData(JOB_EXECUTIONS_DATA_KEY, response.content)
                                        .withStatusLoaded()
                                        .getComponentState()
                                ),
                                map((state) => // NOSONAR
                                    obsoleteStatus === LOADED
                                        ? ComponentUpdate.of(state)
                                        : ComponentLoaded.of(state)
                                )
                            );
                        }),
                        this._handleError(model, task)
                    )
            )
        );
    }

    private _getLatestModel(componentModel: ComponentModel): Observable<ComponentModel> {
        const componentState = componentModel.getComponentState();

        return this.componentService
                   .getModel(componentState.id, componentState.routePathSegments, ['*'])
                   .pipe(
                       take(1)
                   );
    }

    private _handleError(obsoleteModel: ComponentModel, task: DataJobLoadTasks | string) {
        return catchError<ComponentLoaded | ComponentUpdate, Observable<ComponentFailed>>((error: unknown) =>
            this._getLatestModel(obsoleteModel).pipe(
                map((newModel) =>
                    newModel
                        .withTask(task)
                        .withError(error as Error)
                        .withStatusFailed()
                        .getComponentState()
                ),
                map<ComponentState, ComponentFailed>((state) => ComponentFailed.of(state))
            )
        );
    }
}
