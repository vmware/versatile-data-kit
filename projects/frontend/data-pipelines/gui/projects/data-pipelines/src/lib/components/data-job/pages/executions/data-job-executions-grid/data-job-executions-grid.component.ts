/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ChangeDetectionStrategy, ChangeDetectorRef, Component, HostBinding, Input, OnDestroy, OnInit } from '@angular/core';

import { ClrDatagridSortOrder, ClrDatagridStateInterface } from '@clr/angular';

import { CollectionsUtil } from '@versatiledatakit/shared';

import { FiltersSortManager, FilterSortMutationObserver } from '../../../../../commons';

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

import { DataJobExecutionDurationComparator } from './comparators/execution-duration-comparator';

/**
 * ** Supported filter criteria from Executions grid.
 */
const GRID_SUPPORTED_EXECUTIONS_FILTER_KEY: Array<Partial<ExecutionsFilterCriteria>> = [
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
const GRID_SUPPORTED_EXECUTIONS_SORT_KEY: Array<Partial<ExecutionsSortCriteria>> = [
    SORT_STATUS_KEY,
    SORT_TYPE_KEY,
    SORT_DURATION_KEY,
    SORT_START_TIME_KEY,
    SORT_END_TIME_KEY,
    SORT_ID_KEY,
    SORT_VERSION_KEY
];

@Component({
    selector: 'lib-data-job-executions-grid',
    templateUrl: './data-job-executions-grid.component.html',
    styleUrls: ['./data-job-executions-grid.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DataJobExecutionsGridComponent implements OnInit, OnDestroy {
    @Input() jobExecutions: GridDataJobExecution[];
    @Input() loading = false;

    /**
     * ** Executions filters sort manager injected from parent.
     */
    @Input() filtersSortManager: Readonly<
        FiltersSortManager<ExecutionsFilterCriteria, string, ExecutionsSortCriteria, ClrDatagridSortOrder>
    >;

    @HostBinding('attr.data-cy') public readonly attributeDataCy = 'data-pipelines-data-job-executions';

    // Sorting
    durationComparator = new DataJobExecutionDurationComparator(SORT_DURATION_KEY);
    // End of sorting
    openDeploymentDetailsModal = false;
    jobDeploymentModalData: DataJobDeployment;

    private _filterMutationObserver: FilterSortMutationObserver<
        ExecutionsFilterCriteria,
        string,
        ExecutionsSortCriteria,
        ClrDatagridSortOrder
    >;

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

        this._populateManagerFilters(state);
        this._populateManagerSort(state);

        // update Browser URL once only, for every Grid event
        this.filtersSortManager.updateBrowserUrl();
    }

    /**
     * @inheritDoc
     */
    ngOnInit(): void {
        this._filterMutationObserver = (changes) => {
            if (changes.some(([key]) => [...GRID_SUPPORTED_EXECUTIONS_FILTER_KEY, ...GRID_SUPPORTED_EXECUTIONS_SORT_KEY].includes(key))) {
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
        this.filtersSortManager.deleteMutationObserver(this._filterMutationObserver);
    }

    /**
     * ** Extract filters from grid state.
     *      - use bulk operation to update manager
     * @private
     */
    private _populateManagerFilters(state: ClrDatagridStateInterface): void {
        // when grid has user applied filters
        if (CollectionsUtil.isArray(state.filters)) {
            if (state.filters.length > 0) {
                const newFilterPairs: ExecutionsFilterPairs[] = state.filters.map(
                    (filter: ExecutionsGridFilter) => [filter.property, filter.value] as ExecutionsFilterPairs
                );

                // remove known filters if they are already set in the manager but are missing from grid state
                const filtersForDeletion: ExecutionsFilterPairs[] = GRID_SUPPORTED_EXECUTIONS_FILTER_KEY.filter(
                    (supportedCriteria) =>
                        this.filtersSortManager.hasFilter(supportedCriteria) &&
                        newFilterPairs.findIndex(([criteria]) => supportedCriteria === criteria) === -1
                ).map((supportedCriteria) => [supportedCriteria, null]);

                newFilterPairs.push(...filtersForDeletion);

                this.filtersSortManager.bulkUpdate(newFilterPairs.map(([criteria, value]) => [criteria, value, 'filter']));

                return;
            }
        }

        // when grid doesn't have user applied filters but manager has from previous actions
        if (this.filtersSortManager.hasAnyFilter()) {
            // remove known filters if they are already set in the manager
            const filtersForDeletion = GRID_SUPPORTED_EXECUTIONS_FILTER_KEY.filter((criteria) =>
                this.filtersSortManager.hasFilter(criteria)
            ).map((criteria) => [criteria, null] as ExecutionsFilterPairs);

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

            return;
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
}
