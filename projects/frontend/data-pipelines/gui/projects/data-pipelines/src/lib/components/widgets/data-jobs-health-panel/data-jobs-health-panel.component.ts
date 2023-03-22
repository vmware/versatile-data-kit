/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
    Component,
    EventEmitter,
    Inject,
    Input,
    OnInit,
    Output,
} from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import {
    ApiPredicate,
    CollectionsUtil,
    ComponentModel,
    ComponentService,
    DESC,
    ErrorRecord,
    NavigationService,
    OnTaurusModelChange,
    OnTaurusModelError,
    OnTaurusModelInit,
    OnTaurusModelLoad,
    RouterService,
    TaurusBaseComponent,
} from '@versatiledatakit/shared';

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
    TEAM_NAME_REQ_PARAM,
} from '../../../model';

import {
    TASK_LOAD_JOB_EXECUTIONS,
    TASK_LOAD_JOBS_STATE,
} from '../../../state/tasks';
import {
    LOAD_JOB_ERROR_CODES,
    LOAD_JOBS_ERROR_CODES,
} from '../../../state/error-codes';

import { DataJobExecutionToGridDataJobExecution } from '../../data-job/pages/executions';

enum State {
    loading = 'loading',
    ready = 'ready',
    empty = 'empty',
    error = 'error',
}

@Component({
    selector: 'lib-data-jobs-health-panel',
    templateUrl: './data-jobs-health-panel.component.html',
    styleUrls: ['./data-jobs-health-panel.component.scss'],
})
export class DataJobsHealthPanelComponent
    extends TaurusBaseComponent
    implements
        OnInit,
        OnTaurusModelInit,
        OnTaurusModelLoad,
        OnTaurusModelChange,
        OnTaurusModelError
{
    @Input() manageLink: string;
    @Output() componentStateEvent = new EventEmitter<string>();

    readonly uuid = 'DataJobsHealthPanelComponent';

    loadingJobs = true;
    loadingExecutions = true;

    teamName: string;
    loading = true;
    dataJobs: DataJob[];
    jobExecutions: DataJobExecutions;

    /**
     * ** Flag that indicates there is jobs executions load error.
     */
    isComponentInErrorState = false;

    /**
     * ** Array of error code patterns that component should listen for in errors store.
     */
    listenForErrorPatterns: string[] = [
        LOAD_JOB_ERROR_CODES[TASK_LOAD_JOB_EXECUTIONS].All,
        LOAD_JOBS_ERROR_CODES[TASK_LOAD_JOBS_STATE].All,
    ];

    constructor(
        componentService: ComponentService,
        navigationService: NavigationService,
        activatedRoute: ActivatedRoute,
        private readonly routerService: RouterService,
        private readonly dataJobsService: DataJobsService,
        @Inject(DATA_PIPELINES_CONFIGS)
        public readonly dataPipelinesModuleConfig: DataPipelinesConfig,
    ) {
        super(componentService, navigationService, activatedRoute);
    }

    fetchDataJobs(): void {
        this.loadingJobs = true;
        const filters: ApiPredicate[] = [];

        if (this.teamName) {
            filters.push({
                property: 'config.team',
                pattern: this.teamName,
                sort: null,
            });
        }

        this.dataJobsService.loadJobs(
            this.model
                .withRequestParam(TEAM_NAME_REQ_PARAM, 'no-team-specified')
                .withRequestParam(JOB_NAME_REQ_PARAM, '')
                .withFilter(filters)
                .withRequestParam(ORDER_REQ_PARAM, {
                    property: 'startTime',
                    direction: DESC,
                })
                .withPage(1, 1000),
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
                .withRequestParam(FILTER_REQ_PARAM, {
                    statusIn: [
                        DataJobExecutionStatus.USER_ERROR,
                        DataJobExecutionStatus.PLATFORM_ERROR,
                    ],
                    startTimeGte: d,
                    teamNameIn: this.teamName ? [this.teamName] : [],
                } as DataJobExecutionFilter)
                .withRequestParam(ORDER_REQ_PARAM, {
                    property: 'startTime',
                    direction: DESC,
                } as DataJobExecutionOrder),
        );
    }

    /**
     * @inheritDoc
     */
    onModelInit(): void {
        this._subscribeForTeamChange();
        this._emitNewState();
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
            const executions: DataJobExecutions = model
                .getComponentState()
                .data.get(JOB_EXECUTIONS_DATA_KEY);
            if (executions) {
                const remappedExecutions =
                    DataJobExecutionToGridDataJobExecution.convertToDataJobExecution(
                        [...executions],
                    );
                this.jobExecutions = remappedExecutions.filter(
                    (ex) => ex.status !== DataJobExecutionStatus.SUCCEEDED,
                );
                this.loadingExecutions = false;
            }
        } else if (task === TASK_LOAD_JOBS_STATE) {
            const componentState = model.getComponentState();
            const dataJobsData: DataJobPage =
                componentState.data.get(JOBS_DATA_KEY);

            this.dataJobs = CollectionsUtil.isArray(dataJobsData?.content)
                ? [...dataJobsData?.content]
                : [];
            this.loadingJobs = false;
        }

        this._emitNewState();
    }

    /**
     * @inheritDoc
     */
    onModelError(
        model: ComponentModel,
        task: string,
        newErrorRecords: ErrorRecord[],
    ): void {
        newErrorRecords.forEach((errorRecord) => {
            const error = ErrorUtil.extractError(errorRecord.error);

            if (task === TASK_LOAD_JOB_EXECUTIONS) {
                this.jobExecutions = [];
                this.loadingExecutions = false;
            } else if (task === TASK_LOAD_JOBS_STATE) {
                this.loadingJobs = false;
            }

            // don't show toast message, only log to console, logic for component is to stay hidden when there is no data are there is error

            console.error(error);
        });
    }

    /**
     * @inheritDoc
     */
    override ngOnInit(): void {
        // attach listener to ErrorStore and listen for Errors change
        this.errors.onChange((store) => {
            // if there is record for listened error code patterns set component in error state
            this.isComponentInErrorState = store.hasCodePattern(
                ...this.listenForErrorPatterns,
            );
        });

        super.ngOnInit();
    }

    private _emitNewState() {
        if (this.loadingJobs || this.loadingExecutions) {
            this.componentStateEvent.emit(State.loading);
        } else if (
            this.jobExecutions.length === 0 &&
            this.dataJobs.length === 0
        ) {
            this.componentStateEvent.emit(State.empty);
        } else if (this.isComponentInErrorState) {
            this.componentStateEvent.emit(State.error);
        } else {
            this.componentStateEvent.emit(State.ready);
        }
    }

    private _subscribeForTeamChange(): void {
        if (
            this.dataPipelinesModuleConfig.manageConfig
                ?.selectedTeamNameObservable
        ) {
            this.subscriptions.push(
                this.dataPipelinesModuleConfig.manageConfig?.selectedTeamNameObservable.subscribe(
                    {
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
                        },
                    },
                ),
            );
        } else {
            this.fetchDataJobExecutions();
            this.fetchDataJobs();
        }
    }
}
