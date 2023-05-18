/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { DatePipe, Location } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

import { distinctUntilChanged, map } from 'rxjs/operators';

import { ClrDatagridSortOrder } from '@clr/angular';

import {
    ASC,
    CollectionsUtil,
    ComponentModel,
    ComponentService,
    ErrorHandlerService,
    ErrorRecord,
    NavigationService,
    OnTaurusModelChange,
    OnTaurusModelError,
    OnTaurusModelInit,
    OnTaurusModelLoad,
    RouterService,
    RouteState,
    TaurusBaseComponent,
    URLStateManager
} from '@versatiledatakit/shared';

import { DataJobUtil, ErrorUtil } from '../../../../../shared/utils';

import { FiltersSortManager } from '../../../../../commons';

import {
    DataJobExecutionFilter,
    DataJobExecutionOrder,
    DataJobExecutions,
    DataPipelinesRouteData,
    FILTER_REQ_PARAM,
    JOB_EXECUTIONS_DATA_KEY,
    JOB_NAME_REQ_PARAM,
    ORDER_REQ_PARAM,
    TEAM_NAME_REQ_PARAM
} from '../../../../../model';

import { TASK_LOAD_JOB_EXECUTIONS } from '../../../../../state/tasks';

import { LOAD_JOB_ERROR_CODES } from '../../../../../state/error-codes';

import { DataJobsService } from '../../../../../services';

import { DataJobExecutionToGridDataJobExecution, GridDataJobExecution } from '../model/data-job-execution';

import {
    ExecutionsFilterCriteria,
    ExecutionsFilterSortObject,
    ExecutionsSortCriteria,
    SORT_START_TIME_KEY,
    SUPPORTED_EXECUTIONS_FILTER_CRITERIA,
    SUPPORTED_EXECUTIONS_SORT_CRITERIA
} from '../model/executions-filters.model';

@Component({
    selector: 'lib-data-job-executions-page',
    templateUrl: './data-job-executions-page.component.html',
    styleUrls: ['./data-job-executions-page.component.scss'],
    providers: [DatePipe]
})
export class DataJobExecutionsPageComponent
    extends TaurusBaseComponent
    implements OnTaurusModelInit, OnTaurusModelLoad, OnTaurusModelChange, OnTaurusModelError, OnInit, OnDestroy
{
    readonly uuid = 'DataJobExecutionsPageComponent';

    teamName: string;
    jobName: string;
    isJobEditable = false;

    jobExecutions: GridDataJobExecution[];
    minJobExecutionTime: Date;
    loading = true;
    initialLoading = true;

    dateTimeFilter: { fromTime: Date; toTime: Date } = {
        fromTime: null,
        toTime: null
    };

    /**
     * ** Array of error code patterns that component should listen for in errors store.
     */
    listenForErrorPatterns: string[] = [LOAD_JOB_ERROR_CODES[TASK_LOAD_JOB_EXECUTIONS].All];

    /**
     * ** Flag that indicates there is jobs executions load error.
     */
    isComponentInErrorState = false;

    /**
     * ** Executions filters sort manager for this page, that is injected to its children.
     *
     *      - Singleton for the page instance including its children.
     */
    readonly filtersSortManager: Readonly<
        FiltersSortManager<ExecutionsFilterCriteria, string, ExecutionsSortCriteria, ClrDatagridSortOrder>
    >;

    /**
     * ** Url state manager in context of this page.
     *
     *      - Singleton for the page instance including its children.
     */
    private readonly urlStateManager: URLStateManager;

    /**
     * ** Constructor.
     */
    constructor(
        componentService: ComponentService,
        navigationService: NavigationService,
        activatedRoute: ActivatedRoute,
        private readonly routerService: RouterService,
        private readonly dataJobsService: DataJobsService,
        private readonly errorHandlerService: ErrorHandlerService,
        private readonly changeDetectorRef: ChangeDetectorRef,
        private readonly router: Router,
        private readonly location: Location,
        private readonly datePipe: DatePipe
    ) {
        super(componentService, navigationService, activatedRoute);

        this.urlStateManager = new URLStateManager(router.url.split('?')[0], location);
        this.filtersSortManager = new FiltersSortManager(
            this.urlStateManager,
            SUPPORTED_EXECUTIONS_FILTER_CRITERIA,
            SUPPORTED_EXECUTIONS_SORT_CRITERIA
        );
    }

    doNavigateBack(): void {
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        this.navigateBack({ '$.team': this.teamName }).then();
    }

    onTimeFilterChange(dateTimeFilter: { fromTime: Date; toTime: Date }): void {
        this.dateTimeFilter = dateTimeFilter;

        const modelFilter: DataJobExecutionFilter = this.model.getComponentState().requestParams.get(FILTER_REQ_PARAM) ?? {};

        if (CollectionsUtil.isNil(dateTimeFilter.fromTime) || CollectionsUtil.isNil(dateTimeFilter.toTime)) {
            delete modelFilter.startTimeGte;
            delete modelFilter.startTimeLte;

            this.model.withRequestParam(FILTER_REQ_PARAM, {
                ...modelFilter
            } as DataJobExecutionFilter);
        } else {
            this.model.withRequestParam(FILTER_REQ_PARAM, {
                ...modelFilter,
                startTimeGte: dateTimeFilter.fromTime,
                startTimeLte: dateTimeFilter.toTime
            } as DataJobExecutionFilter);
        }

        this.fetchDataJobExecutions();
    }

    fetchDataJobExecutions(): void {
        this.loading = true;

        this.dataJobsService.loadJobExecutions(
            this.model
                .withRequestParam(TEAM_NAME_REQ_PARAM, this.teamName)
                .withRequestParam(JOB_NAME_REQ_PARAM, this.jobName)
                .withRequestParam(ORDER_REQ_PARAM, {
                    property: 'startTime',
                    direction: ASC
                } as DataJobExecutionOrder)
        );

        this.changeDetectorRef.markForCheck();
    }

    /**
     * @inheritDoc
     */
    onModelInit(): void {
        let isInitialized = false;

        this.subscriptions.push(
            this.routerService
                .getState()
                .pipe(
                    distinctUntilChanged((a, b) => {
                        return CollectionsUtil.isEqual(a.queryParams, b.queryParams);
                    })
                )
                .subscribe((state) => {
                    if (!isInitialized) {
                        isInitialized = true;

                        this._initialize(state);
                    } else {
                        // pass query params for popped state and let manager extract known filters and sort
                        // action is needed for Browser backward/forward actions that trigger router navigation
                        // tested only for "locationToUrl" update strategy for URLStateManager
                        this.filtersSortManager.bulkUpdate(state.queryParams as ExecutionsFilterSortObject, true);
                    }
                })
        );
    }

    /**
     * @inheritDoc
     */
    onModelLoad(): void {
        this.loading = false;
        this.initialLoading = false;
    }

    /**
     * @inheritDoc
     */
    onModelChange(model: ComponentModel, task: string): void {
        if (task === TASK_LOAD_JOB_EXECUTIONS) {
            const executions: DataJobExecutions = model.getComponentState().data.get(JOB_EXECUTIONS_DATA_KEY);
            if (executions) {
                this.dataJobsService.notifyForJobExecutions([...executions]);

                // eslint-disable-next-line @typescript-eslint/unbound-method
                const runningExecution = executions.find(DataJobUtil.isJobRunningPredicate);
                if (runningExecution) {
                    this.dataJobsService.notifyForRunningJobExecutionId(runningExecution.id);
                }
            }
        }
    }

    /**
     * @inheritDoc
     */
    onModelError(model: ComponentModel, _task: string, newErrorRecords: ErrorRecord[]): void {
        newErrorRecords.forEach((errorRecord) => {
            const error = ErrorUtil.extractError(errorRecord.error);

            this.errorHandlerService.processError(error);
        });
    }

    /**
     * @inheritDoc
     */
    override ngOnInit(): void {
        // attach listener to ErrorStore and listen for Errors change
        this.errors.onChange((store) => {
            // if there is record for listened error code patterns set component in error state
            this.isComponentInErrorState = store.hasCodePattern(...this.listenForErrorPatterns);
        });

        super.ngOnInit();
    }

    /**
     * @inheritDoc
     */
    override ngOnDestroy(): void {
        this.filtersSortManager.cancelScheduledBrowserUrlUpdate();

        super.ngOnDestroy();
    }

    private _initialize(state: RouteState): void {
        const teamParamKey = state.getData<DataPipelinesRouteData['teamParamKey']>('teamParamKey');
        this.teamName = state.getParam(teamParamKey);

        const jobParamKey = state.getData<DataPipelinesRouteData['jobParamKey']>('jobParamKey');
        this.jobName = state.getParam(jobParamKey);

        this.isJobEditable = !!state.getData<DataPipelinesRouteData['editable']>('editable');

        // filters/sort manager have to be initialized before sending HTTP request to load executions
        this._initializeFiltersSortManager(state);

        this._subscribeForExecutions();

        this.fetchDataJobExecutions();
    }

    private _initializeFiltersSortManager(state: RouteState): void {
        // update manager configuration
        this.filtersSortManager.changeBaseUrl(state.absoluteRoutePath);
        this.filtersSortManager.changeUpdateStrategy('locationToURL');

        // update stored filters and sort criteria from Browser URL query params
        this.filtersSortManager.bulkUpdate(state.queryParams as ExecutionsFilterSortObject);

        // if there is no sort applied through Browser URL, apply default sorting by Start Time Descending
        if (!this.filtersSortManager.hasAnySort()) {
            this.filtersSortManager.setSort(SORT_START_TIME_KEY, ClrDatagridSortOrder.DESC);
        }

        // update Browser URL with replace state, normalized to only manager known criteria
        this.filtersSortManager.updateBrowserUrl('replaceToURL', true);
    }

    private _subscribeForExecutions(): void {
        this.subscriptions.push(
            this.dataJobsService
                .getNotifiedForJobExecutions()
                .pipe(map(DataJobExecutionToGridDataJobExecution.convertToDataJobExecution(this.datePipe)))
                .subscribe({
                    next: (values) => {
                        this.jobExecutions = values.filter((ex) => {
                            if (CollectionsUtil.isNil(this.dateTimeFilter.fromTime) || CollectionsUtil.isNil(this.dateTimeFilter.toTime)) {
                                return true;
                            }

                            if (!CollectionsUtil.isString(ex.startTime)) {
                                return false;
                            }

                            const startTime = new Date(ex.startTime);

                            return startTime > this.dateTimeFilter.fromTime && startTime < this.dateTimeFilter.toTime;
                        });

                        if (this.jobExecutions.length > 0) {
                            const newMinJobExecutionsTime = new Date(
                                this.jobExecutions.reduce((prev, curr) => (prev.startTime < curr.startTime ? prev : curr)).startTime
                            );

                            if (
                                CollectionsUtil.isNil(this.minJobExecutionTime) ||
                                newMinJobExecutionsTime.getTime() - this.minJobExecutionTime.getTime() !== 0
                            ) {
                                this.minJobExecutionTime = newMinJobExecutionsTime;
                            }
                        }
                    },
                    error: (error: unknown) => {
                        console.error(error);
                    }
                })
        );
    }
}
