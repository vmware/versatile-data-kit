/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Inject, Input, Output } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import {
    ApiPredicate,
    CollectionsUtil,
    ComponentModel,
    ComponentService,
    DESC,
    ErrorHandlerService,
    NavigationService,
    OnTaurusModelChange,
    OnTaurusModelError,
    OnTaurusModelInit,
    OnTaurusModelLoad,
    RouterService,
    TaurusBaseComponent
} from '@vdk/shared';

import { ErrorUtil } from '../../../shared/utils';

import { DataJobsService } from '../../../services';
import {
    DATA_PIPELINES_CONFIGS,
    DataJob,
    DataJobExecutionFilter,
    DataJobExecutionOrder,
    DataJobExecutions,
    DataJobExecutionStatus,
    DataJobPage,
    DataPipelinesConfig,
    FILTER_REQ_PARAM,
    JOB_EXECUTIONS_DATA_KEY,
    JOB_NAME_REQ_PARAM,
    JOBS_DATA_KEY,
    ORDER_REQ_PARAM,
    TEAM_NAME_REQ_PARAM
} from '../../../model';
import { TASK_LOAD_JOB_EXECUTIONS } from '../../../state/tasks';

import { DataJobExecutionToGridDataJobExecution } from '../../data-job/pages/executions';

enum State {
    loading = 'loading',
    ready = 'ready',
    empty = 'empty'
}

@Component({
    selector: 'lib-data-jobs-health-panel',
    templateUrl: './data-jobs-health-panel.component.html',
    styleUrls: ['./data-jobs-health-panel.component.scss']
})
export class DataJobsHealthPanelComponent extends TaurusBaseComponent
    implements OnTaurusModelInit, OnTaurusModelLoad, OnTaurusModelChange, OnTaurusModelError {

    @Input() manageLink: string;
    @Output() componentStateEvent = new EventEmitter<string>();

    readonly uuid = 'DataJobsHealthPanelComponent';

    loadingJobs = true;
    loadingExecutions = true;

    teamName: string;
    loading = true;
    dataJobs: DataJob[];
    jobExecutions: DataJobExecutions;

    constructor(
        componentService: ComponentService,
        navigationService: NavigationService,
        activatedRoute: ActivatedRoute,
        private readonly routerService: RouterService,
        private readonly dataJobsService: DataJobsService,
        private readonly errorHandlerService: ErrorHandlerService,
        @Inject(DATA_PIPELINES_CONFIGS) public readonly dataPipelinesModuleConfig: DataPipelinesConfig) {
        super(componentService, navigationService, activatedRoute);
    }

    fetchDataJobs(): void {
        this.loadingJobs = true;
        const filters: ApiPredicate[] = [];

        if (this.teamName) {
            filters.push({
                property: 'config.team',
                pattern: this.teamName,
                sort: null
            });
        }

        this.dataJobsService.loadJobs(
            this.model
                .withRequestParam(TEAM_NAME_REQ_PARAM, 'no-team-specified')
                .withRequestParam(JOB_NAME_REQ_PARAM, '')
                .withFilter(filters)
                .withRequestParam(ORDER_REQ_PARAM, { property: 'startTime', direction: DESC })
                .withPage(1, 1000)
        );
    }

    fetchDataJobExecutions(): void {
        this.loadingExecutions = true;
        const d = new Date();
        d.setDate(d.getDate() - 1);
        this.dataJobsService.loadJobExecutions(
            this.model
                .withRequestParam(TEAM_NAME_REQ_PARAM, 'no-team-specified')
                .withRequestParam(JOB_NAME_REQ_PARAM, '')
                .withRequestParam(
                    FILTER_REQ_PARAM,
                    {
                        statusIn: [DataJobExecutionStatus.USER_ERROR, DataJobExecutionStatus.PLATFORM_ERROR],
                        startTimeGte: d,
                        teamNameIn: this.teamName ? [this.teamName] : []
                    } as DataJobExecutionFilter
                )
                .withRequestParam(ORDER_REQ_PARAM, { property: 'startTime', direction: DESC } as DataJobExecutionOrder)
        );
    }

    /**
     * @inheritDoc
     */
    onModelInit(): void {
        this._subscribeForTeamChange();
        this.emitNewState();
    }

    /**
     * @inheritDoc
     */
    onModelLoad(): void {
        this.loading = false;
    }

    /**
     * @inheritDoc
     */
    onModelChange(model: ComponentModel, task: string): void {
        if (task === TASK_LOAD_JOB_EXECUTIONS) {
            const executions: DataJobExecutions = model.getComponentState().data.get(JOB_EXECUTIONS_DATA_KEY);
            if (executions) {
                const remappedExecutions = DataJobExecutionToGridDataJobExecution.convertToDataJobExecution([...executions]);
                this.jobExecutions = remappedExecutions.filter((ex) => ex.status !== DataJobExecutionStatus.SUCCEEDED);
                this.loadingExecutions = false;
            }
        } else {
            const componentState = model.getComponentState();
            const dataJobsData: DataJobPage = componentState.data.get(JOBS_DATA_KEY);

            this.dataJobs = CollectionsUtil.isArray(dataJobsData?.content)
                ? [...dataJobsData?.content]
                : [];
            this.loadingJobs = false;
        }
        this.emitNewState();
    }

    /**
     * @inheritDoc
     */
    onModelError(model: ComponentModel, task: string): void {
        if (task === TASK_LOAD_JOB_EXECUTIONS) {
            this.jobExecutions = [];
            this.loadingExecutions = false;
        } else {
            this.loadingJobs = false;
        }

        const error = ErrorUtil.extractError(
            model.getComponentState().error
        );

        this.errorHandlerService.processError(error);
    }

    private emitNewState() {
        if (this.loadingJobs || this.loadingExecutions) {
            this.componentStateEvent.emit(State.loading);
        } else if (this.jobExecutions.length === 0 && this.dataJobs.length === 0) {
            this.componentStateEvent.emit(State.empty);
        } else {
            this.componentStateEvent.emit(State.ready);
        }
    }

    private _subscribeForTeamChange(): void {
        if (this.dataPipelinesModuleConfig.manageConfig?.selectedTeamNameObservable) {
            this.subscriptions.push(
                this.dataPipelinesModuleConfig.manageConfig?.selectedTeamNameObservable
                    .subscribe({
                        next: (newTeamName: string) => {
                            if (newTeamName !== this.teamName) {
                                if (newTeamName && newTeamName !== '') {
                                    this.teamName = newTeamName;
                                    this.fetchDataJobExecutions();
                                    this.fetchDataJobs();
                                }
                            }
                        },
                        error: (error: unknown) => {
                            this.jobExecutions = [];
                            this.dataJobs = [];
                            console.error('Error loading selected team', error);
                        }
                    })
            );
        } else {
            this.fetchDataJobExecutions();
            this.fetchDataJobs();
        }
    }
}
