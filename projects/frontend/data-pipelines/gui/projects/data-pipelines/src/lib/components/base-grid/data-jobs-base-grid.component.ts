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
    GridFilters,
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
    filter: GridFilters;
    sort: { [key: string]: ClrDatagridSortOrder };
    search: string;
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

    /**
     * ** Update strategy that will be used to update Browser URL.
     *
     *      - 'updateLocation' will update softly update the URL using Location service, and it's default one
     *      - 'updateRouter' will trigger Angular router resolve mechanism with all guards and resolvers through Router service
     */
    @Input() urlUpdateStrategy: 'updateLocation' | 'updateRouter' = 'updateLocation';

    /**
     * ** Query param key for search value.
     */
    @Input() searchParam: string = QUERY_PARAM_SEARCH;
    /**
     * ** Position for search query param.
     */
    @Input() searchParamPosition = 0;

    /**
     * ** Base position index for Data Jobs filters query param.
     *
     *      - Every filter has its own defined +x from the base.
     */
    @Input() filtersQueryParamPositionBase = 0;

    /**
     * ** URLStateManager external dependency injection to act in synchronous way external pages and the Data Jobs.
     */
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

    dataJobStatus = DataJobStatus;

    initializingComponent = true;

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
        this.clrGridUIState.search = value;

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
            // While the teamNameFilter is empty, no refresh requests will be executed.
            console.warn('Refresh operation will be skipped. teamNameFilter is empty.');

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
        let previousState: RouteState;

        this.subscriptions.push(
            this.routerService
                .get()
                .pipe(
                    distinctUntilChanged(
                        (a, b) =>
                            (a.state.absoluteConfigPath !== b.state.absoluteConfigPath ||
                                a.state.absoluteRoutePath === b.state.absoluteRoutePath) &&
                            this._areQueryParamsPristine(b.state)
                    )
                )
                .subscribe((routerState) => {
                    if (initializationFinished) {
                        // check if route state comes from Browser popped state (Browser stack)
                        if (
                            (!previousState || previousState.absoluteRoutePath === routerState.state.absoluteRoutePath) &&
                            !this._areQueryParamsPristine(routerState.state)
                        ) {
                            this._extractQueryParams(routerState.state);
                            this._updateUrlStateManager();

                            // set query params mutation to false, because it's Browser popped state
                            // no need to update the Browser URL, just URLStateManager need to be updated
                            this.urlStateManager.isQueryParamsStateMutated = false;
                        } else {
                            this._updateUrlStateManager(routerState.state);
                        }

                        previousState = routerState.state;

                        return;
                    }

                    initializationFinished = true;
                    previousState = routerState.state;

                    this._initUrlStateManager(routerState.state);
                    this._extractQueryParams(routerState.state);

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

        if (this.initializingComponent) {
            this.initializingComponent = false;
        }
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

                    this._initializeQuickFilters();
                    this._updateUrlStateManager();

                    if (this.restoreUIStateInProgress) {
                        this._doUrlUpdate('replaceLocation');
                    }
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
                .withSearch(this.clrGridUIState.search)
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

    private _extractQueryParams(routeState: RouteState): void {
        if (!routeState.queryParams) {
            this.clrGridUIState.search = '';
            this.clrGridUIState.filter = {};

            return;
        }

        if (!this.initializingComponent) {
            this.clrGridUIState.filter.jobName = routeState.getQueryParam('jobName');
            this.clrGridUIState.filter.teamName = routeState.getQueryParam('teamName');
            this.clrGridUIState.filter.description = routeState.getQueryParam('description');
            this.clrGridUIState.filter.deploymentStatus = this._decodeFilterFromQueryParam(
                'deploymentStatus',
                routeState.getQueryParam('deploymentStatus')
            );
            this.clrGridUIState.filter.deploymentLastExecutionStatus = this._decodeFilterFromQueryParam(
                'deploymentLastExecutionStatus',
                routeState.getQueryParam('deploymentLastExecutionStatus')
            );
        } else {
            this._checkMutatedFilterAndUpdate(routeState, 'jobName', false);
            this._checkMutatedFilterAndUpdate(routeState, 'teamName', false);
            this._checkMutatedFilterAndUpdate(routeState, 'description', false);

            this._checkMutatedFilterAndUpdate(routeState, 'deploymentStatus', true);
            this._checkMutatedFilterAndUpdate(routeState, 'deploymentLastExecutionStatus', true);
        }

        // search has different handling so because of that is last handled
        const searchQueryString = routeState.getQueryParam(this.searchParam);
        const normalizedSearchQueryString = searchQueryString ? searchQueryString : '';
        if (this.clrGridUIState.search !== normalizedSearchQueryString) {
            this.search(normalizedSearchQueryString);
        }
    }

    private _updateUrlStateManager(routeState?: RouteState): void {
        if (CollectionsUtil.isDefined(routeState)) {
            this.urlStateManager.baseURL = routeState.absoluteRoutePath;
        }

        this.urlStateManager.setQueryParam('jobName', this.clrGridUIState.filter.jobName, this.filtersQueryParamPositionBase + 1);
        this.urlStateManager.setQueryParam('teamName', this.clrGridUIState.filter.teamName, this.filtersQueryParamPositionBase + 2);
        this.urlStateManager.setQueryParam('description', this.clrGridUIState.filter.description, this.filtersQueryParamPositionBase + 3);
        this.urlStateManager.setQueryParam(
            'deploymentStatus',
            this._encodeFilterForQueryParam('deploymentStatus', this.clrGridUIState.filter.deploymentStatus),
            this.filtersQueryParamPositionBase + 4
        );
        this.urlStateManager.setQueryParam(
            'deploymentLastExecutionStatus',
            this._encodeFilterForQueryParam('deploymentLastExecutionStatus', this.clrGridUIState.filter.deploymentLastExecutionStatus),
            this.filtersQueryParamPositionBase + 5
        );

        // search has different handling so because of that is last handled
        this.urlStateManager.setQueryParam(this.searchParam, this.clrGridUIState.search, this.searchParamPosition);
    }

    private _areQueryParamsPristine(routeState: RouteState): boolean {
        if (this.clrGridUIState.search !== routeState.getQueryParam(this.searchParam)) {
            return false;
        }

        if (this.clrGridUIState.filter.jobName !== routeState.getQueryParam('jobName')) {
            return false;
        }

        if (this.clrGridUIState.filter.teamName !== routeState.getQueryParam('teamName')) {
            return false;
        }

        if (this.clrGridUIState.filter.description !== routeState.getQueryParam('description')) {
            return false;
        }

        if (
            this.clrGridUIState.filter.deploymentStatus !==
            this._decodeFilterFromQueryParam('deploymentStatus', routeState.getQueryParam('deploymentStatus'))
        ) {
            return false;
        }

        return (
            this.clrGridUIState.filter.deploymentLastExecutionStatus ===
            this._decodeFilterFromQueryParam('deploymentLastExecutionStatus', routeState.getQueryParam('deploymentLastExecutionStatus'))
        );
    }

    private _checkMutatedFilterAndUpdate(routeState: RouteState, key: keyof GridFilters, decode: boolean): void {
        if (!decode) {
            if (
                CollectionsUtil.isDefined(routeState.getQueryParam(key)) &&
                this.clrGridUIState.filter[key] !== routeState.getQueryParam(key)
            ) {
                this.clrGridUIState.filter[key] = routeState.getQueryParam(key);
            }
        } else {
            if (
                CollectionsUtil.isDefined(
                    routeState.getQueryParam(key) &&
                        this.clrGridUIState.filter[key] !== this._decodeFilterFromQueryParam(key, routeState.getQueryParam(key))
                )
            ) {
                this.clrGridUIState.filter[key] = this._decodeFilterFromQueryParam(key, routeState.getQueryParam(key));
            }
        }
    }

    private _doUrlUpdate(strategy: 'updateLocation' | 'updateRouter' | 'replaceLocation' = this.urlUpdateStrategy): void {
        if (strategy === 'updateLocation') {
            this.urlStateManager.locationToURL();
        } else if (strategy === 'updateRouter') {
            // eslint-disable-next-line @typescript-eslint/no-floating-promises
            this.urlStateManager.navigateToUrl().then();
        } else {
            this.urlStateManager.replaceToUrl();
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
                    pattern: this._createApiFilterPattern(property, value),
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

    private _encodeFilterForQueryParam(propertyName: keyof GridFilters, value: string): string {
        switch (propertyName) {
            case 'deploymentStatus':
                if (CollectionsUtil.isNil(value)) {
                    return 'all';
                }

                return `${value}`.replace(' ', '_').toLowerCase();
            case 'deploymentLastExecutionStatus':
                if (CollectionsUtil.isNil(value)) {
                    return undefined;
                }

                return `${value}`.toLowerCase();
            default:
                return `${value}`.toLowerCase();
        }
    }

    private _decodeFilterFromQueryParam(propertyName: keyof GridFilters, value: string): string {
        switch (propertyName) {
            case 'deploymentStatus':
                switch (value) {
                    case 'enabled':
                        return DataJobStatus.ENABLED;
                    case 'disabled':
                        return DataJobStatus.DISABLED;
                    case 'not_deployed':
                        return DataJobStatus.NOT_DEPLOYED;
                    default:
                        return undefined;
                }
            case 'deploymentLastExecutionStatus':
                if (CollectionsUtil.isNil(value)) {
                    return undefined;
                }

                const normalizedExecStatus: DataJobExecutionStatus = `${value}`.toUpperCase() as DataJobExecutionStatus;

                return this.executionStatuses.includes(normalizedExecStatus) ? normalizedExecStatus : undefined;
            default:
                return `${value}`.toLowerCase();
        }
    }

    private _createApiFilterPattern(propertyName: string, value: string) {
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
            this.clrGridUIState.filter.deploymentStatus = status;
        };

        const deactivateFilter = () => {
            delete this.clrGridUIState.filter.deploymentStatus;
        };

        const isActiveQuickFilter = (status: DataJobStatus | 'all'): boolean => {
            if (status === 'all') {
                return CollectionsUtil.isNil(this.clrGridUIState.filter.deploymentStatus);
            }

            return this.clrGridUIState.filter.deploymentStatus === status;
        };

        const filters: QuickFilters = [
            {
                label: 'All',
                suppressCancel: true,
                active: isActiveQuickFilter('all'),
                onActivate: deactivateFilter
            },
            {
                label: 'Enabled',
                active: isActiveQuickFilter(DataJobStatus.ENABLED),
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
                active: isActiveQuickFilter(DataJobStatus.DISABLED),
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
                active: isActiveQuickFilter(DataJobStatus.NOT_DEPLOYED),
                onActivate: activateFilter(DataJobStatus.NOT_DEPLOYED),
                onDeactivate: deactivateFilter,
                icon: {
                    title: 'Not Deployed - This job is created but still not deployed',
                    shape: 'circle',
                    size: 15
                }
            }
        ];

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
            },
            search: ''
        };
    }
}
