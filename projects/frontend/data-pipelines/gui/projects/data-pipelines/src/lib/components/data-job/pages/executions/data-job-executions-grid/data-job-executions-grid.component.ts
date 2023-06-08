/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
    ChangeDetectionStrategy,
    ChangeDetectorRef,
    Component,
    EventEmitter,
    HostBinding,
    Input,
    OnChanges,
    OnDestroy,
    OnInit,
    Output,
    SimpleChanges
} from '@angular/core';

import { ClrDatagridSortOrder, ClrDatagridStateInterface } from '@clr/angular';

import { AndCriteria, CollectionsUtil, Comparator, Criteria } from '@versatiledatakit/shared';

import { FilterSortMutationObserver, FiltersSortManager } from '../../../../../commons';

import { DataJobDeployment } from '../../../../../model';

import {
    ExecutionsFilterCriteria,
    ExecutionsFilterPairs,
    ExecutionsGridFilter,
    ExecutionsSortCriteria,
    ExecutionsSortPairs,
    FILTER_DURATION_KEY,
    FILTER_END_TIME_KEY,
    FILTER_ID_KEY,
    FILTER_START_TIME_KEY,
    FILTER_STATUS_KEY,
    FILTER_TYPE_KEY,
    FILTER_VERSION_KEY,
    GridDataJobExecution,
    SORT_DURATION_KEY,
    SORT_END_TIME_KEY,
    SORT_ID_KEY,
    SORT_START_TIME_KEY,
    SORT_STATUS_KEY,
    SORT_TYPE_KEY,
    SORT_VERSION_KEY
} from '../model';

import { ExecutionsStatusCriteria, ExecutionsStringCriteria, ExecutionsTypeCriteria } from './criteria';
import { ExecutionDefaultComparator, ExecutionDurationComparator } from './comparators';

/**
 * ** Supported filter criteria from Executions grid.
 */
const GRID_SUPPORTED_EXECUTIONS_FILTER_KEY: Array<GridExecutionFilterCriteria> = [
    FILTER_STATUS_KEY,
    FILTER_TYPE_KEY,
    FILTER_DURATION_KEY,
    FILTER_START_TIME_KEY,
    FILTER_END_TIME_KEY,
    FILTER_ID_KEY,
    FILTER_VERSION_KEY
];

/**
 * ** Supported sort criteria from Executions grid.
 */
const GRID_SUPPORTED_EXECUTIONS_SORT_KEY: Array<GridExecutionSortCriteria> = [
    SORT_STATUS_KEY,
    SORT_TYPE_KEY,
    SORT_DURATION_KEY,
    SORT_START_TIME_KEY,
    SORT_END_TIME_KEY,
    SORT_ID_KEY,
    SORT_VERSION_KEY
];

type GridExecutionFilterCriteria = Exclude<ExecutionsFilterCriteria, 'timePeriod'>;
type GridExecutionsFilterPairs = ExecutionsFilterPairs<GridExecutionFilterCriteria>;

type GridExecutionSortCriteria = Exclude<ExecutionsSortCriteria, 'timePeriod'>;
type GridExecutionsSortPairs = ExecutionsFilterPairs<GridExecutionSortCriteria>;

type GridStateLocal = {
    filter: GridExecutionsFilterPairs[];
    sort: ExecutionsSortPairs;
};

export interface GridCriteriaAndComparator {
    filter: Criteria<GridDataJobExecution>;
    sort: Comparator<GridDataJobExecution>;
}

@Component({
    selector: 'lib-data-job-executions-grid',
    templateUrl: './data-job-executions-grid.component.html',
    styleUrls: ['./data-job-executions-grid.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DataJobExecutionsGridComponent implements OnChanges, OnInit, OnDestroy {
    @Input() jobExecutions: GridDataJobExecution[];
    @Input() loading = false;

    /**
     * ** Executions filters sort manager injected from parent.
     */
    @Input() filtersSortManager: Readonly<
        FiltersSortManager<ExecutionsFilterCriteria, string, ExecutionsSortCriteria, ClrDatagridSortOrder>
    >;

    /**
     * ** If provided will try to highlight row where execution id will match.
     */
    @Input() highlightedExecutionId: string;

    /**
     * ** Event Emitter that emits events on every user action on grid filters or sort.
     */
    @Output() gridCriteriaAndComparatorChanged: EventEmitter<GridCriteriaAndComparator> = new EventEmitter<GridCriteriaAndComparator>();

    @HostBinding('attr.data-cy') public readonly attributeDataCy = 'data-pipelines-data-job-executions';

    openDeploymentDetailsModal = false;
    jobDeploymentModalData: DataJobDeployment;

    paginatedJobExecutions: GridDataJobExecution[] = [];

    paginationPageNumber: number;
    paginationPageSize: number;
    paginationTotalItems: number;

    isInitialCriteriasEmit = true;

    private _appliedGridState: GridStateLocal = {
        filter: [],
        sort: undefined
    };
    private _previousAppliedGridState: GridStateLocal = {
        filter: [],
        sort: undefined
    };

    private _filterMutationObserver: FilterSortMutationObserver<
        ExecutionsFilterCriteria,
        string,
        ExecutionsSortCriteria,
        ClrDatagridSortOrder
    >;

    /**
     * ** Reference to scheduled timeout for emitting Grid Criteria and Comparator.
     * @private
     */
    private _gridCriteriaAndComparatorEmitterTimeoutRef: number;

    /**
     * ** Constructor.
     */
    constructor(private readonly changeDetectorRef: ChangeDetectorRef) {}

    /**
     * ** NgFor elements tracking function.
     */
    trackByFn(index: number, execution: GridDataJobExecution): string {
        return `${index}|${execution?.id}`;
    }

    showDeploymentDetails(jobExecution: GridDataJobExecution) {
        this.openDeploymentDetailsModal = true;
        this.jobDeploymentModalData = jobExecution.deployment;

        this.changeDetectorRef.detectChanges();
    }

    /**
     * ** Main callback (listener) for ClrGrid state mutation, like filters, sort.
     */
    gridRefresh(state: ClrDatagridStateInterface): void {
        if (!state) {
            return;
        }

        let skipCriteriaAndComparatorEmitterDebouncing = false;

        if (this.isInitialCriteriasEmit) {
            this.isInitialCriteriasEmit = false;
            skipCriteriaAndComparatorEmitterDebouncing = true;
        }

        this._populateManagerFilters(state);
        this._populateManagerSort(state);
        this._evaluateGridStateMutation(skipCriteriaAndComparatorEmitterDebouncing);

        this._paginateExecutions(state);

        // update Browser URL once only, for every Grid event
        this.filtersSortManager.updateBrowserUrl();
    }

    /**
     * @inheritDoc
     */
    ngOnChanges(changes: SimpleChanges): void {
        if (
            changes['jobExecutions'] &&
            !CollectionsUtil.isEqual(changes['jobExecutions'].previousValue, changes['jobExecutions'].currentValue)
        ) {
            this.paginationTotalItems = this.jobExecutions.length;
            this._paginateExecutions(null);
        }
    }

    /**
     * @inheritDoc
     */
    ngOnInit(): void {
        this._filterMutationObserver = (changes) => {
            if (
                changes.some(([key]: GridExecutionsSortPairs) =>
                    [...GRID_SUPPORTED_EXECUTIONS_FILTER_KEY, ...GRID_SUPPORTED_EXECUTIONS_SORT_KEY].includes(key)
                )
            ) {
                this.changeDetectorRef.markForCheck();
            }
        };

        // register callback that would listen for mutation of supported filter and sort criteria
        this.filtersSortManager.registerMutationObserver(this._filterMutationObserver);
    }

    /**
     * @inheritDoc
     */
    ngOnDestroy(): void {
        if (CollectionsUtil.isNumber(this._gridCriteriaAndComparatorEmitterTimeoutRef)) {
            clearTimeout(this._gridCriteriaAndComparatorEmitterTimeoutRef);
        }

        this.filtersSortManager.deleteMutationObserver(this._filterMutationObserver);
    }

    /**
     * ** Extract filters from grid state.
     *      - use bulk operation to update manager
     * @private
     */
    private _populateManagerFilters(state: ClrDatagridStateInterface): void {
        // on every grid emitted event save currently applied filters for comparison
        this._previousAppliedGridState.filter = [...this._appliedGridState.filter];

        // when grid has user applied filters
        if (CollectionsUtil.isArray(state.filters)) {
            if (state.filters.length > 0) {
                const newFilterPairs: GridExecutionsFilterPairs[] = state.filters.map(
                    (filter: ExecutionsGridFilter) => [filter.property, filter.value] as GridExecutionsFilterPairs
                );

                // remove known filters if they are already set in the manager but are missing from grid state
                const filtersForDeletion: GridExecutionsFilterPairs[] = GRID_SUPPORTED_EXECUTIONS_FILTER_KEY.filter(
                    (supportedCriteria) =>
                        this.filtersSortManager.hasFilter(supportedCriteria) &&
                        newFilterPairs.findIndex(([criteria]) => supportedCriteria === criteria) === -1
                ).map((supportedCriteria) => [supportedCriteria, null]);

                newFilterPairs.push(...filtersForDeletion);

                this.filtersSortManager.bulkUpdate(newFilterPairs.map(([criteria, value]) => [criteria, value, 'filter']));

                // set new filters to applied grid filters state
                this._appliedGridState.filter = [...newFilterPairs];

                return;
            }
        } else {
            // clear applied grid filters state
            this._appliedGridState.filter = [];
        }

        // when grid doesn't have user applied filters but manager has from previous actions
        if (this.filtersSortManager.hasAnyFilter()) {
            // remove known filters if they are already set in the manager
            const filtersForDeletion = GRID_SUPPORTED_EXECUTIONS_FILTER_KEY.filter((criteria) =>
                this.filtersSortManager.hasFilter(criteria)
            ).map((criteria) => [criteria, null] as GridExecutionsFilterPairs);

            if (filtersForDeletion.length > 0) {
                this.filtersSortManager.bulkUpdate(filtersForDeletion.map(([criteria, value]) => [criteria, value, 'filter']));
            }
        }
    }

    /**
     * ** Extract sort criteria and direction from grid state and update the manager
     * @private
     */
    private _populateManagerSort(state: ClrDatagridStateInterface): void {
        // on every grid emitted event save currently applied sort pair
        this._previousAppliedGridState.sort = this._appliedGridState.sort;

        // when grid has user applied sort
        if (CollectionsUtil.isDefined(state.sort)) {
            const property: ExecutionsSortCriteria = CollectionsUtil.isStringWithContent(state.sort.by)
                ? (state.sort.by as ExecutionsSortCriteria)
                : (state.sort.by as unknown as { property: ExecutionsSortCriteria })?.property;
            const direction = state.sort.reverse ? ClrDatagridSortOrder.DESC : ClrDatagridSortOrder.ASC;
            const newSortPairs: ExecutionsSortPairs[] = [[property, direction]];

            // always remove known previous stored sort criteria and direction
            // manager supports multi sort, but grid support single sort only
            // remove known sorts if they are already set in the manager but are missing from grid state
            const sortsForDeletion: ExecutionsSortPairs[] = GRID_SUPPORTED_EXECUTIONS_SORT_KEY.filter(
                (supportedCriteria) =>
                    this.filtersSortManager.hasSort(supportedCriteria) &&
                    newSortPairs.findIndex(([criteria]) => supportedCriteria === criteria) === -1
            ).map((supportedCriteria) => [supportedCriteria, null]);

            newSortPairs.push(...sortsForDeletion);

            this.filtersSortManager.bulkUpdate(newSortPairs.map(([criteria, value]) => [criteria, value, 'sort']));

            // set new sort to applied grid sort state
            this._appliedGridState.sort = newSortPairs[0];

            return;
        } else {
            // clear applied grid sort state
            this._appliedGridState.sort = undefined;
        }

        // when grid doesn't have user applied sort but manager has from previous actions
        if (this.filtersSortManager.hasAnySort()) {
            // remove known sort if they are already set in the manager
            const sortsForDeletion = GRID_SUPPORTED_EXECUTIONS_SORT_KEY.filter((criteria) => this.filtersSortManager.hasSort(criteria)).map(
                (criteria) => [criteria, null] as ExecutionsSortPairs
            );

            if (sortsForDeletion.length > 0) {
                this.filtersSortManager.bulkUpdate(sortsForDeletion.map(([criteria, value]) => [criteria, value, 'sort']));
            }
        }
    }

    private _paginateExecutions(state: ClrDatagridStateInterface): void {
        this.paginationPageNumber = state?.page?.current ?? 1;
        this.paginationPageSize = state?.page?.size ?? 10;

        const pageSize = CollectionsUtil.isDefined(this.paginationPageSize) ? this.paginationPageSize : 10;
        const pageNumber = CollectionsUtil.isDefined(this.paginationPageNumber) ? this.paginationPageNumber - 1 : 0;
        const from = pageNumber * pageSize;
        const to = (pageNumber + 1) * pageSize;

        this.paginatedJobExecutions = this.jobExecutions.slice(from, to);
    }

    private _evaluateGridStateMutation(skipDebouncing = false): void {
        if (
            this._previousAppliedGridState.filter.length !== this._appliedGridState.filter.length ||
            this._previousAppliedGridState.sort !== this._appliedGridState.sort
        ) {
            this._emitGridCriteriaAndComparator(skipDebouncing);

            return;
        }

        if (this._previousAppliedGridState.filter.length === this._appliedGridState.filter.length) {
            if (!CollectionsUtil.isEqual(this._previousAppliedGridState.filter, this._appliedGridState.filter)) {
                this._emitGridCriteriaAndComparator(skipDebouncing);

                return;
            }
        }

        if (!CollectionsUtil.isEqual(this._previousAppliedGridState.sort, this._appliedGridState.sort)) {
            this._emitGridCriteriaAndComparator(skipDebouncing);

            return;
        }
    }

    private _emitGridCriteriaAndComparator(skipDebouncing = false): void {
        if (CollectionsUtil.isNumber(this._gridCriteriaAndComparatorEmitterTimeoutRef)) {
            clearTimeout(this._gridCriteriaAndComparatorEmitterTimeoutRef);

            this._gridCriteriaAndComparatorEmitterTimeoutRef = null;
        }

        if (skipDebouncing) {
            this.gridCriteriaAndComparatorChanged.emit({
                filter: this._createFilterCriteria(),
                sort: this._createSortComparator()
            });

            return;
        }

        this._gridCriteriaAndComparatorEmitterTimeoutRef = setTimeout(() => {
            this.gridCriteriaAndComparatorChanged.emit({
                filter: this._createFilterCriteria(),
                sort: this._createSortComparator()
            });

            this._gridCriteriaAndComparatorEmitterTimeoutRef = null;
        }, 200);
    }

    private _createFilterCriteria(): Criteria<GridDataJobExecution> {
        const criteria: Criteria<GridDataJobExecution>[] = [];

        for (const filterPair of this._appliedGridState.filter) {
            if (filterPair[0] === 'status') {
                criteria.push(new ExecutionsStatusCriteria(filterPair[1]));

                continue;
            }

            if (filterPair[0] === 'type') {
                criteria.push(new ExecutionsTypeCriteria(filterPair[1]));

                continue;
            }

            if (filterPair[0] === 'startTime') {
                criteria.push(new ExecutionsStringCriteria('startTimeFormatted', filterPair[1]));

                continue;
            }

            if (filterPair[0] === 'endTime') {
                criteria.push(new ExecutionsStringCriteria('endTimeFormatted', filterPair[1]));

                continue;
            }

            criteria.push(new ExecutionsStringCriteria(filterPair[0], filterPair[1]));
        }

        return criteria.length > 0 ? new AndCriteria(...criteria) : null;
    }

    private _createSortComparator(): Comparator<GridDataJobExecution> {
        if (CollectionsUtil.isDefined(this._appliedGridState.sort)) {
            const [sortCriteria, sortValue] = this._appliedGridState.sort;

            if (sortCriteria === 'duration') {
                return new ExecutionDurationComparator(sortValue === ClrDatagridSortOrder.ASC ? 'ASC' : 'DESC');
            }

            return new ExecutionDefaultComparator(sortCriteria, sortValue === ClrDatagridSortOrder.ASC ? 'ASC' : 'DESC');
        }

        return null;
    }
}
