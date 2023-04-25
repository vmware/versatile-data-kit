/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable @typescript-eslint/naming-convention,@angular-eslint/directive-class-suffix */

import { Directive, ElementRef, Input, OnInit } from '@angular/core';
import { Location } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, take } from 'rxjs/operators';

import { ClrDatagridSortOrder, ClrDatagridStateInterface } from '@clr/angular';

import {
    ApiPredicate,
    ASC,
    CollectionsUtil,
    ComponentModel,
    ComponentService,
    DESC,
    ErrorHandlerService,
    ErrorRecord,
    NavigationService,
    OnTaurusModelChange,
    OnTaurusModelError,
    OnTaurusModelInit,
    OnTaurusModelInitialLoad,
    OnTaurusModelLoad,
    RouterService,
    RouterState,
    RouteState,
    TaurusBaseComponent,
    URLStateManager
} from '@versatiledatakit/shared';

import { ErrorUtil } from '../../shared/utils';

import { QuickFilters } from '../../shared/components';

import {
    DataJob,
    DataJobExecutionStatus,
    DataJobStatus,
    DataPipelinesConfig,
    DataPipelinesRestoreUI,
    DisplayMode,
    JOBS_DATA_KEY
} from '../../model';

import { TASK_LOAD_JOBS_STATE } from '../../state/tasks';

import { LOAD_JOBS_ERROR_CODES } from '../../state/error-codes';

import { DataJobsApiService, DataJobsService } from '../../services';

export const QUERY_PARAM_SEARCH = 'search';

export type ClrGridUIState = {
    totalItems: number;
    lastPage: number;
    pageSize: number;
    filter: { [key: string]: string };
    sort: { [key: string]: ClrDatagridSortOrder };
};

export type UIElementOffset = { x: number; y: number };

export type DataJobsLocalStorageUserConfig = {
    hiddenColumns: { [columnName: string]: boolean };
};

@Directive()
export abstract class DataJobsBaseGridComponent
    extends TaurusBaseComponent
    implements OnInit, OnTaurusModelInit, OnTaurusModelInitialLoad, OnTaurusModelLoad, OnTaurusModelChange, OnTaurusModelError
{
    /**
     * @inheritDoc
     */
    static override readonly CLASS_NAME: string = 'DataJobsBaseGridComponent';

    /**
     * @inheritDoc
     */
    static override readonly PUBLIC_NAME: string = 'DataJobs-BaseGrid-Component';

    static readonly UI_KEY_PAGE_OFFSET = 'pageOffset';
    static readonly UI_KEY_GRID_OFFSET = 'gridOffset';
    static readonly UI_KEY_GRID_UI_STATE = 'gridUIState';

    static readonly CONTENT_AREA_SELECTOR = '.content-area';
    static readonly DATA_GRID_SELECTOR = '.datagrid';

    @Input() urlUpdateStrategy: 'updateLocation' | 'updateRouter' = 'updateRouter';
    @Input() searchParam: string = QUERY_PARAM_SEARCH;

    @Input() set urlStateManager(value: URLStateManager) {
        if (value) {
            this._urlStateManager = value;
            this._isUrlStateManagerExternalDependency = true;
        }
    }

    get urlStateManager(): URLStateManager {
        return this._urlStateManager;
    }

    teamNameFilter: string;
    displayMode = DisplayMode.STANDARD;

    filterByTeamName = false;

    searchQueryValue = '';
    selectedJob: DataJob;
    gridState: ClrDatagridStateInterface;
    loading = false;

    dataJobs: DataJob[] = [];
    totalJobs = 0;
    loadDataDebouncer = new Subject<'normal' | 'forced'>();

    deploymentStatuses = [DataJobStatus.ENABLED, DataJobStatus.DISABLED, DataJobStatus.NOT_DEPLOYED];
    executionStatuses = [
        DataJobExecutionStatus.SUCCEEDED,
        DataJobExecutionStatus.PLATFORM_ERROR,
        DataJobExecutionStatus.USER_ERROR,
        DataJobExecutionStatus.SKIPPED,
        DataJobExecutionStatus.CANCELLED
    ];

    clrGridCurrentPage = 1;
    clrGridUIState: ClrGridUIState;
    clrGridDefaultFilter: ClrGridUIState['filter'];
    clrGridDefaultSort: ClrGridUIState['sort'];

    quickFilters: QuickFilters;
    quickFiltersDefaultActiveIndex: number;

    dataJobStatus = DataJobStatus;

    /**
     * ** Array of error code patterns that component should listen for in errors store.
     */
    listenForErrorPatterns: string[] = [LOAD_JOBS_ERROR_CODES[TASK_LOAD_JOBS_STATE].All];

    /**
     * ** Flag that indicates actionable elements should be disabled.
     */
    disableActionableElements = false;

    protected restoreUIStateInProgress = false;
    protected navigationInProgress = false;
    protected _urlStateManager: URLStateManager;

    private _isUrlStateManagerExternalDependency = false;

    protected constructor(
        componentService: ComponentService,
        navigationService: NavigationService,
        activatedRoute: ActivatedRoute,
        protected readonly routerService: RouterService,
        protected readonly dataJobsService: DataJobsService,
        protected readonly dataJobsApiService: DataJobsApiService,
        protected readonly errorHandlerService: ErrorHandlerService,
        protected readonly location: Location,
        protected readonly router: Router,
        protected readonly elementRef: ElementRef<HTMLElement>,
        protected readonly document: Document,
        protected dataPipelinesModuleConfig: DataPipelinesConfig,
        protected readonly localStorageConfigKey: string,
        public localStorageUserConfig: DataJobsLocalStorageUserConfig,
        className: string = null
    ) {
        super(componentService, navigationService, activatedRoute, className ?? DataJobsBaseGridComponent.CLASS_NAME);

        this._urlStateManager = new URLStateManager(router.url.split('?')[0], location);
    }

    /**
     * ** NgFor elements tracking function.
     */
    trackByFn(index: number, dataJob: DataJob): string {
        return `${index}|${dataJob?.config?.team}|${dataJob?.jobName}`;
    }

    resolveLogsUrl(job: DataJob): string {
        if (CollectionsUtil.isNil(job) || CollectionsUtil.isArrayEmpty(job.deployments)) {
            return null;
        }

        if (CollectionsUtil.isArrayEmpty(job.deployments[0].executions)) {
            return null;
        }

        return job.deployments[0].executions[0].logsUrl;
    }

    showOrHideColumnChange(columnName: string, hidden: boolean): void {
        this.localStorageUserConfig.hiddenColumns[columnName] = hidden;
        localStorage.setItem(this.localStorageConfigKey, JSON.stringify(this.localStorageUserConfig));
    }

    getJobStatus(job: DataJob): DataJobExecutionStatus {
        if (job.deployments && job.deployments[0]?.lastExecutionStatus) {
            return job.deployments[0]?.lastExecutionStatus;
        }

        return null;
    }

    getJobSuccessRateTitle(job: DataJob): string {
        if (job.deployments) {
            return `${job.deployments[0]?.successfulExecutions} successful / ${
                job.deployments[0]?.failedExecutions + job.deployments[0]?.successfulExecutions
            } total`;
        }

        return null;
    }

    /**
     * ** Callback (listener) for User search.
     */
    search(value: string) {
        this.searchQueryValue = value;

        this._updateUrlStateManager();

        this.refresh();
    }

    refresh(): void {
        this.loadDataWithState(null);
    }

    /**
     * ** Main callback (listener) for ClrGrid state mutation, like filters, sort.
     */
    loadDataWithState(state: ClrDatagridStateInterface): void {
        if (state != null) {
            this.gridState = state;
        }

        if (!this.model || this.restoreUIStateInProgress) {
            return;
        }

        if (this.filterByTeamName && !this.teamNameFilter) {
            //While the teamNameFilter is empty, no refresh requests will be executed.
            console.log('Refresh operation will be skipped. teamNameFilter is empty.');

            return;
        }

        this.loadDataDebouncer.next('normal');
    }

    isStandardDisplayMode() {
        return this.displayMode === DisplayMode.STANDARD;
    }

    selectionChanged(dataJob: DataJob) {
        this.selectedJob = dataJob;
    }

    /**
     * ** Navigate to Data Job details page, while at first save Ui State of the Page.
     */
    navigateToJobDetails(job?: DataJob) {
        if (job) {
            this.saveUIState();
            this.selectionChanged(job);

            this.dataJobsService.notifyForTeamImplicitly(job.config?.team);

            this.navigationInProgress = true;

            this.navigateTo({
                '$.team': job.config?.team,
                '$.job': job.jobName
            }).finally(() => {
                this.navigationInProgress = false;
            });
        }
    }

    /**
     * @inheritDoc
     */
    onModelInit(): void {
        let initializationFinished = false;

        this.subscriptions.push(
            this.routerService
                .get()
                .pipe(
                    distinctUntilChanged(
                        (a, b) =>
                            a.state.absoluteConfigPath !== b.state.absoluteConfigPath ||
                            a.state.absoluteRoutePath === b.state.absoluteRoutePath
                    )
                )
                .subscribe((routerState) => {
                    if (initializationFinished) {
                        this._updateUrlStateManager(routerState.state);

                        return;
                    }

                    initializationFinished = true;

                    this._initUrlStateManager(routerState.state);
                    this._extractInitialQueryParams(routerState.state);

                    if (this._doesRestoreUIStateExist()) {
                        if (this._shouldRestoreUIState(routerState)) {
                            this.restoreUIStateInProgress = true;

                            const clrGridUIState = this.model.getUiState<ClrGridUIState>(DataJobsBaseGridComponent.UI_KEY_GRID_UI_STATE);
                            if (clrGridUIState) {
                                this.clrGridUIState = clrGridUIState;
                            }

                            this.loadDataDebouncer.next('forced');

                            return;
                        } else {
                            this._clearUiPageState();
                        }
                    }

                    if (this.gridState) {
                        this.refresh();
                    }
                })
        );
    }

    /**
     * @inheritDoc
     */
    onModelInitialLoad(): void {
        this.routerService
            .get()
            .pipe(take(1))
            .subscribe((routerState) => {
                if (this._shouldRestoreUIState(routerState)) {
                    this.restoreUIState();

                    this.restoreUIStateInProgress = false;
                }
            });
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
    onModelChange(model: ComponentModel): void {
        this._extractData(model);
    }

    /**
     * @inheritDoc
     */
    onModelError(model: ComponentModel, _task: string, newErrorRecords: ErrorRecord[]): void {
        this._extractData(model);

        newErrorRecords.forEach((errorRecord) => {
            const error = ErrorUtil.extractError(errorRecord.error);

            this.errorHandlerService.processError(error);
        });
    }

    /**
     * @inheritDoc
     */
    override ngOnInit(): void {
        this._initializeQuickFilters();
        this._initializeClrGridUIState();

        // attach listener to ErrorStore and listen for Errors change
        this.errors.onChange((store) => {
            // if there is record for listened error code patterns disable actionable elements
            this.disableActionableElements = store.hasCodePattern(...this.listenForErrorPatterns);
        });

        this.subscriptions.push(
            this.loadDataDebouncer.pipe(debounceTime(300)).subscribe((handling) => {
                if (this.isLoadDataAllowed() || handling === 'forced') {
                    this._doLoadData();
                }

                if (this.isUrlUpdateAllowed() || handling === 'forced') {
                    this._doUrlUpdate();
                }
            })
        );

        super.ngOnInit();

        this.loading = true;

        try {
            this._loadLocalStorageUserConfig();
        } catch (e1) {
            console.error('Failed to read config from localStorage', e1, 'Will attempt to re-create it.');
            try {
                localStorage.removeItem(this.localStorageConfigKey);
                this._loadLocalStorageUserConfig();
            } catch (e2) {
                console.error('Was unable to re-initialize localStorage user config', e2);
            }
        }
    }

    protected isLoadDataAllowed(): boolean {
        if (!this.gridState) {
            //While the gridState is empty, no refresh requests will be executed.
            console.log('Load data will be skipped. gridState is empty. operation not allowed.');

            return false;
        }

        return !this.navigationInProgress;
    }

    protected isUrlUpdateAllowed(): boolean {
        return !this.navigationInProgress && this.urlStateManager.isQueryParamsStateMutated;
    }

    protected saveUIState() {
        const dataGrid = this.elementRef.nativeElement.querySelector(DataJobsBaseGridComponent.DATA_GRID_SELECTOR);
        if (dataGrid) {
            this.model.withUiState(DataJobsBaseGridComponent.UI_KEY_GRID_OFFSET, {
                x: dataGrid.scrollLeft,
                y: dataGrid.scrollTop
            });
        }

        const contentArea = this.document.querySelector(DataJobsBaseGridComponent.CONTENT_AREA_SELECTOR);
        if (contentArea) {
            this.model.withUiState(DataJobsBaseGridComponent.UI_KEY_PAGE_OFFSET, {
                x: contentArea.scrollLeft,
                y: contentArea.scrollTop
            });
        }

        const clrGridUIStateDeepCloned = CollectionsUtil.cloneDeep(this.clrGridUIState);
        clrGridUIStateDeepCloned.pageSize = this.model.getComponentState()?.page?.size;
        clrGridUIStateDeepCloned.lastPage = this.clrGridCurrentPage;

        this.model.withUiState(DataJobsBaseGridComponent.UI_KEY_GRID_UI_STATE, clrGridUIStateDeepCloned);

        this.componentService.update(this.model.getComponentState());
    }

    protected restoreUIState() {
        if (!this._doesRestoreUIStateExist()) {
            return;
        }

        setTimeout(() => {
            const gridOffset = this.model.getUiState<UIElementOffset>(DataJobsBaseGridComponent.UI_KEY_GRID_OFFSET);
            const dataGrid = this.elementRef.nativeElement.querySelector(DataJobsBaseGridComponent.DATA_GRID_SELECTOR);
            if (dataGrid) {
                dataGrid.scrollTo(gridOffset.x, gridOffset.y);
            }

            const pageOffset = this.model.getUiState<UIElementOffset>(DataJobsBaseGridComponent.UI_KEY_PAGE_OFFSET);
            const contentArea = this.document.querySelector(DataJobsBaseGridComponent.CONTENT_AREA_SELECTOR);
            if (contentArea) {
                contentArea.scrollTo(pageOffset.x, pageOffset.y);
            }

            this._clearUiPageState();
        }, 25);
    }

    private _shouldRestoreUIState(routerState: RouterState): boolean {
        const restoreUiWhen = routerState.state.getData<DataPipelinesRestoreUI>('restoreUiWhen');
        if (CollectionsUtil.isNil(restoreUiWhen)) {
            return true;
        }

        if (!CollectionsUtil.isString(restoreUiWhen.previousConfigPathLike)) {
            return true;
        }

        return routerState.getPrevious().state.absoluteConfigPath.includes(restoreUiWhen.previousConfigPathLike);
    }

    private _doesRestoreUIStateExist(): boolean {
        return (
            CollectionsUtil.isDefined(this.model) &&
            CollectionsUtil.isDefined(this.model.getUiState<ClrGridUIState>(DataJobsBaseGridComponent.UI_KEY_GRID_UI_STATE))
        );
    }

    private _clearUiPageState() {
        this.model.getComponentState().uiState.delete(DataJobsBaseGridComponent.UI_KEY_GRID_OFFSET);
        this.model.getComponentState().uiState.delete(DataJobsBaseGridComponent.UI_KEY_PAGE_OFFSET);
        this.model.getComponentState().uiState.delete(DataJobsBaseGridComponent.UI_KEY_GRID_UI_STATE);

        this.componentService.update(this.model.getComponentState());
    }

    private _doLoadData(): void {
        this.selectedJob = null;
        this.loading = true;

        if (this._doesRestoreUIStateExist()) {
            this.clrGridCurrentPage = this.clrGridUIState.lastPage;
        } else {
            this.model
                .withFilter(this._buildRefreshFilters())
                .withSearch(this.searchQueryValue)
                .withPage(this.gridState?.page?.current, this.gridState?.page?.size);
        }

        this.dataJobsService.loadJobs(this.model);
    }

    private _extractData(model: ComponentModel): void {
        const componentState = model.getComponentState();
        const dataJobsData: { content?: DataJob[]; totalItems?: number } = componentState.data.get(JOBS_DATA_KEY) ?? {};

        this.dataJobs = CollectionsUtil.isArray(dataJobsData?.content) ? [...dataJobsData?.content] : [];

        this.clrGridUIState.totalItems = dataJobsData?.totalItems ?? 0;
    }

    private _initUrlStateManager(routeState: RouteState): void {
        if (!this._isUrlStateManagerExternalDependency) {
            this._urlStateManager = new URLStateManager(routeState.absoluteRoutePath, this.location);
        }
    }

    private _extractInitialQueryParams(routeState: RouteState): void {
        const initialSearchParams = routeState.getQueryParam(this.searchParam);

        if (initialSearchParams) {
            this.searchQueryValue = initialSearchParams;

            this._updateUrlStateManager();
        } else {
            this.searchQueryValue = '';
        }
    }

    private _updateUrlStateManager(routeState?: RouteState): void {
        if (CollectionsUtil.isDefined(routeState)) {
            this.urlStateManager.baseURL = routeState.absoluteRoutePath;
        }

        this.urlStateManager.setQueryParam(this.searchParam, this.searchQueryValue);
    }

    private _doUrlUpdate(): void {
        if (this.urlUpdateStrategy === 'updateLocation') {
            this.urlStateManager.locationToURL();
        } else {
            // eslint-disable-next-line @typescript-eslint/no-floating-promises
            this.urlStateManager.navigateToUrl().then();
        }
    }

    private _loadLocalStorageUserConfig() {
        const userConfig = localStorage.getItem(this.localStorageConfigKey);
        if (userConfig) {
            let newColumnProvided = false;
            const parsedUserConfig: DataJobsLocalStorageUserConfig = JSON.parse(userConfig);

            CollectionsUtil.iterateObject(this.localStorageUserConfig.hiddenColumns, (value, key) => {
                if (!parsedUserConfig.hiddenColumns.hasOwnProperty(key)) {
                    newColumnProvided = true;
                    parsedUserConfig.hiddenColumns[key] = value;
                }
            });

            if (newColumnProvided) {
                localStorage.setItem(this.localStorageConfigKey, JSON.stringify(parsedUserConfig));
            }

            this.localStorageUserConfig = parsedUserConfig;
        } else {
            localStorage.setItem(this.localStorageConfigKey, JSON.stringify(this.localStorageUserConfig));
        }
    }

    /**
     * ** Builds refresh filters.
     *
     *      - Convert filters from an array to map, because that's what backend-calling service is expecting
     */
    private _buildRefreshFilters(): ApiPredicate[] {
        const filters: ApiPredicate[] = [];

        if (this.teamNameFilter) {
            filters.push({
                property: 'config.team',
                pattern: this.teamNameFilter,
                sort: null
            });
        }

        if (this.gridState?.filters) {
            for (const _filter of this.gridState.filters) {
                const { property, value } = _filter as {
                    property: string;
                    value: string;
                };

                filters.push({
                    property,
                    pattern: this._getFilterPattern(property, value),
                    sort: null
                });
            }
        }

        if (this.gridState?.sort) {
            const direction = this.gridState.sort.reverse ? DESC : ASC;

            filters.push({
                property: this.gridState.sort.by as string,
                pattern: null,
                sort: direction
            });
        }

        return filters;
    }

    private _getFilterPattern(propertyName: string, value: string) {
        // TODO: Remove this, once the Backend support % filterting for all the properties
        // TODO: Once jobName get the same handling as config.team, add case proper case
        switch (propertyName) {
            case 'config.team':
                return `%${value}%`;
            case 'deployments.enabled':
                return `${value}`.toLowerCase().replace(' ', '_');
            case 'deployments.lastExecutionStatus':
                return `${value}`.toLowerCase();
            case 'jobName':
                return `*${value}*`;
            default:
                return `${value}`;
        }
    }

    private _initializeQuickFilters(): void {
        const activateFilter = (status: DataJobStatus) => () => {
            this.clrGridUIState.filter['deployments.enabled'] = status;
        };

        const deactivateFilter = () => {
            delete this.clrGridUIState.filter['deployments.enabled'];
        };

        const filters: QuickFilters = [
            {
                label: 'All',
                suppressCancel: true,
                onActivate: () => {
                    this.clrGridUIState.filter = {};
                }
            },
            {
                label: 'Enabled',
                onActivate: activateFilter(DataJobStatus.ENABLED),
                onDeactivate: deactivateFilter,
                icon: {
                    title: 'Enabled - This job is deployed and executed by schedule',
                    class: 'is-solid status-icon-enabled',
                    shape: 'check-circle',
                    size: 20
                }
            },
            {
                label: 'Disabled',
                onActivate: activateFilter(DataJobStatus.DISABLED),
                onDeactivate: deactivateFilter,
                icon: {
                    title: 'Disabled - This job is deployed but not executing by schedule',
                    class: 'is-solid status-icon-disabled',
                    shape: 'times-circle',
                    size: 15
                }
            },
            {
                label: 'Not Deployed',
                onActivate: activateFilter(DataJobStatus.NOT_DEPLOYED),
                onDeactivate: deactivateFilter,
                icon: {
                    title: 'Not Deployed - This job is created but still not deployed',
                    shape: 'circle',
                    size: 15
                }
            }
        ];

        if (
            CollectionsUtil.isNumber(this.quickFiltersDefaultActiveIndex) &&
            CollectionsUtil.isDefined(filters[this.quickFiltersDefaultActiveIndex])
        ) {
            filters[this.quickFiltersDefaultActiveIndex].active = true;
        }

        this.quickFilters = filters;
    }

    private _initializeClrGridUIState(): void {
        this.clrGridUIState = {
            totalItems: 0,
            lastPage: 1,
            pageSize: 25,
            filter: {
                ...(this.clrGridDefaultFilter ?? {})
            },
            sort: {
                ...(this.clrGridDefaultSort ?? {})
            }
        };
    }
}
