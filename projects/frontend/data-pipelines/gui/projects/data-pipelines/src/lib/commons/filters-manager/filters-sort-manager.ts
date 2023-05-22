/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { CollectionsUtil, URLStateManager } from '@versatiledatakit/shared';

export const SORT_KEY = 'sort';
export const FILTER_KEY = 'filter';

/**
 * ** Generic key-value (criteria-value) tuple in context of Filters and Sort
 *      with optional 3rd value that clarify the criteria type (either filter or sort).
 *
 *      - 3rd value is very useful if filter and sort criteria overlaps by their names.
 */
export type KeyValueTuple<K extends string | number, V extends string | number> = [
    key: K,
    value: V,
    type?: typeof FILTER_KEY | typeof SORT_KEY
];
/**
 * ** Mutation observer that could be registered in {@link FiltersSortManager}
 *
 *      - Executed whenever mutation is registered in {@link FiltersSortManager} according its algorithm.
 */
export type FilterSortMutationObserver<
    FC extends string,
    FV extends string | number,
    SC extends string = string,
    SV extends string | number = string | number
> = (changes: KeyValueTuple<FC | SC, FV | SV>[]) => void;

/**
 * ** Generic Filters and Sort Manager that takes into account Clarity DataGrid and also Browser URL query params behaviours.
 *
 *      - Leverages {@link URLStateManager} functionalities for Browser URL manipulation.
 */
export class FiltersSortManager<
    FC extends string,
    FV extends string | number,
    SC extends string = string,
    SV extends string | number = string | number
> {
    /**
     * ** Filter criteria and value storage.
     */
    readonly filterCriteria: Record<FC, FV> = {} as Record<FC, FV>;
    /**
     * ** Sort criteria and value storage.
     */
    readonly sortCriteria: Record<SC, SV> = {} as Record<SC, SV>;

    /**
     * ** Update strategy used in {@link URLStateManager}.
     * @private
     */
    private _updateStrategy: 'navigateToUrl' | 'locationToURL' | 'replaceToURL' = 'locationToURL';
    /**
     * ** Debouncing used whenever Browser URL should be updated.
     * @private
     */
    private _debouncingTime = 300; // value is in milliseconds
    /**
     * ** Reference to scheduled timeout in conjunction with {@link _debouncingTime}
     * @private
     */
    private _updateTimeoutRef: number;

    /**
     * ** Mutation observers storage.
     * @private
     */
    private readonly _mutationObservers: Set<FilterSortMutationObserver<FC, FV, SC, SV>> = new Set<
        FilterSortMutationObserver<FC, FV, SC, SV>
    >();

    /**
     * ** Constructor.
     */
    constructor(
        private readonly urlStateManager: URLStateManager,
        private readonly knownFilterCriteria: FC[],
        private readonly knownSortCriteria: SC[]
    ) {}

    /**
     * ** Returns true if requested criteria is found and its value is defined in Manager filter storage {@link filterCriteria}.
     */
    hasFilter(criteria: FC): boolean {
        return this.filterCriteria.hasOwnProperty(criteria) && CollectionsUtil.isDefined(this.filterCriteria[criteria]);
    }

    /**
     * ** Returns true if there is at least one filter with defined value in Manager filter storage {@link filterCriteria}.
     */
    hasAnyFilter(): boolean {
        return CollectionsUtil.objectPairs(this.filterCriteria).filter(([_key, value]) => CollectionsUtil.isDefined(value)).length > 0;
    }

    /**
     * ** Set filter criteria in Manager filter storage {@link filterCriteria}.
     *
     *      - on every filter set, Browser URL is updated with debouncing by default, and mutation observers are notified.
     *      - optionally: Browser URL update could be skipped if 3rd parameter is provided with false value.
     */
    setFilter(criteria: FC, value: string | number, updateBrowserUrl = true): void {
        if (this.filterCriteria[criteria] === value) {
            return;
        }

        if (CollectionsUtil.isDefined(value)) {
            this.filterCriteria[criteria] = `${value}` as FV;
        } else {
            delete this.filterCriteria[criteria];
        }

        this._serializeFilters();

        if (updateBrowserUrl) {
            this.updateBrowserUrl();
        }

        this._notifyMutationObservers([[criteria, value as FV, 'filter']]);
    }

    /**
     * ** Delete filter criteria from Manager filter storage {@link filterCriteria}.
     *
     *      - on every delete filter, Browser URL is updated with debouncing by default, and mutation observers are notified.
     *      - optionally: Browser URL update could be skipped if 2nd parameter is provided with false value.
     */
    deleteFilter(criteria: FC, updateBrowserUrl = true): boolean {
        if (!this.hasFilter(criteria)) {
            return false;
        }

        delete this.filterCriteria[criteria];

        this._serializeFilters();

        if (updateBrowserUrl) {
            this.updateBrowserUrl();
        }

        this._notifyMutationObservers([[criteria, null, 'filter']]);

        return true;
    }

    /**
     * ** Clear all filters criteria from Manager filter storage {@link filterCriteria}.
     *
     *      - on every clear filters, Browser URL is updated with debouncing by default, and mutation observers are notified.
     *      - optionally: Browser URL update could be skipped if 1st parameter is provided with false value.
     *      - optionally: Mutation observers notification could be skipped if 2nd parameter is provided with false value.
     */
    clearFilters(updateBrowserUrl = true, notifyMutationObservers = true): void {
        const filterPairs = CollectionsUtil.objectPairs(this.filterCriteria);
        const mutatedFilterPairs: KeyValueTuple<FC, FV>[] = filterPairs.map(([key]) => [key, null, 'filter'] as KeyValueTuple<FC, FV>);

        filterPairs.forEach(([key]) => {
            delete this.filterCriteria[key];
        });

        this._serializeFilters();

        if (updateBrowserUrl) {
            this.updateBrowserUrl();
        }

        if (notifyMutationObservers) {
            this._notifyMutationObservers(mutatedFilterPairs);
        }
    }

    /**
     * ** Returns true if requested criteria is found and its value is defined in Manager sort storage {@link sortCriteria}.
     */
    hasSort(criteria: SC): boolean {
        return this.sortCriteria.hasOwnProperty(criteria) && CollectionsUtil.isDefined(this.sortCriteria[criteria]);
    }

    /**
     * ** Returns true if there is at least one sort with defined value in Manager sort storage {@link sortCriteria}.
     */
    hasAnySort(): boolean {
        return CollectionsUtil.objectPairs(this.sortCriteria).filter(([_key, value]) => CollectionsUtil.isDefined(value)).length > 0;
    }

    /**
     * ** Set sort criteria in Manager sort storage {@link sortCriteria}.
     *
     *      - on every sort set, Browser URL is updated with debouncing by default, and mutation observers are notified.
     *      - optionally: Browser URL update could be skipped if 3rd parameter is provided with false value.
     */
    setSort(criteria: SC, direction: SV, updateBrowserUrl = true): void {
        if (this.sortCriteria[criteria] === direction) {
            return;
        }

        if (CollectionsUtil.isDefined(direction)) {
            this.sortCriteria[criteria] = direction;
        } else {
            delete this.sortCriteria[criteria];
        }

        this._serializeSort();

        if (updateBrowserUrl) {
            this.updateBrowserUrl();
        }

        this._notifyMutationObservers([[criteria, direction, 'sort']]);
    }

    /**
     * ** Clear all sort criteria from Manager sort storage {@link sortCriteria}.
     *
     *      - on every clear sort, Browser URL is updated with debouncing by default, and mutation observers are notified.
     *      - optionally: Browser URL update could be skipped if 1st parameter is provided with false value.
     *      - optionally: Mutation observers notification could be skipped if 2nd parameter is provided with false value.
     */
    clearSort(updateBrowserUrl = true, notifyMutationObservers = true): void {
        const mutatedSortPairs: KeyValueTuple<SC, SV>[] = [];

        CollectionsUtil.objectPairs(this.sortCriteria).forEach(([key]) => {
            mutatedSortPairs.push([key, null, 'sort']);

            delete this.sortCriteria[key];
        });

        this._serializeSort();

        if (updateBrowserUrl) {
            this.updateBrowserUrl();
        }

        if (notifyMutationObservers) {
            this._notifyMutationObservers(mutatedSortPairs);
        }
    }

    /**
     * ** Clear all filter and sort criteria from Manager storage {@link filterCriteria} {@link sortCriteria}.
     *
     *      - on every clear, Browser URL is updated with debouncing by default, and mutation observers are notified.
     *      - optionally: Browser URL update could be skipped if 1st parameter is provided with false value.
     *      - optionally: Mutation observers notification could be skipped if 2nd parameter is provided with false value.
     */
    clear(updateBrowserUrl = true, notifyMutationObservers = true): void {
        this.clearFilters(updateBrowserUrl, notifyMutationObservers);
        this.clearSort(updateBrowserUrl, notifyMutationObservers);
    }

    /**
     * ** Bulk update Manager storages for filter and sort criteria using key-value (criteria-value) tuples
     *      with optional 3rd value that clarify the criteria type (either filter or sort).
     */
    bulkUpdate(filterSortPairs: KeyValueTuple<FC | SC, FV | SV>[], clearPreviousValues?: boolean);
    /**
     * ** Bulk update Manager storages for filter and sort criteria leveraging provided nested object criteria-value.
     */
    bulkUpdate(filterValues: Record<typeof FILTER_KEY | typeof SORT_KEY, string>, clearPreviousValues?: boolean): void;
    /**
     * @inheritDoc
     */
    bulkUpdate(
        updates: Record<typeof FILTER_KEY | typeof SORT_KEY, string> | KeyValueTuple<FC | SC, FV | SV>[],
        clearPreviousValues = false
    ): void {
        // Nil (null or undefined) skipped execution
        if (CollectionsUtil.isNil(updates)) {
            return;
        }

        // Array means key-value tuples provided
        if (CollectionsUtil.isArray(updates)) {
            const mutatedFilterPairs: KeyValueTuple<FC, FV>[] = this._persistBulkFilters(
                updates as KeyValueTuple<FC, FV>[],
                clearPreviousValues
            );
            this._serializeFilters();

            const mutatedSortPairs: KeyValueTuple<SC, SV>[] = this._persistBulkSort(
                updates as KeyValueTuple<SC, SV>[],
                clearPreviousValues
            );
            this._serializeSort();

            this._notifyMutationObservers([...mutatedFilterPairs, ...mutatedSortPairs]);

            return;
        }

        // otherwise presume it's and object with filter
        if ((updates as object).hasOwnProperty(FILTER_KEY) && CollectionsUtil.isStringWithContent(updates[FILTER_KEY])) {
            const deserializedFilterCriteria = this._deserializeFilters(updates[FILTER_KEY]);
            const normalizedFilterCriteria: KeyValueTuple<FC, FV>[] = CollectionsUtil.objectPairs(deserializedFilterCriteria).map(
                (filterPairs) => [filterPairs[0], filterPairs[1], 'filter'] as unknown as KeyValueTuple<FC, FV>
            );

            const mutatedFilterPairs: KeyValueTuple<FC, FV>[] = this._persistBulkFilters(normalizedFilterCriteria, clearPreviousValues);
            this._serializeFilters();

            this._notifyMutationObservers(mutatedFilterPairs);
        } else if (clearPreviousValues) {
            this.clearFilters(false);
        }

        // otherwise presume it's and object with sort
        if ((updates as object).hasOwnProperty(SORT_KEY) && CollectionsUtil.isStringWithContent(updates[SORT_KEY])) {
            const deserializedSortCriteria = this._deserializeSort(updates[SORT_KEY]);
            const normalizedSortCriteria: KeyValueTuple<SC, SV>[] = CollectionsUtil.objectPairs(deserializedSortCriteria).map(
                (sortPairs) => [sortPairs[0], sortPairs[1], 'sort'] as unknown as KeyValueTuple<SC, SV>
            );

            const mutatedSortPairs: KeyValueTuple<SC, SV>[] = this._persistBulkSort(normalizedSortCriteria, clearPreviousValues);
            this._serializeSort();

            this._notifyMutationObservers(mutatedSortPairs);
        } else if (clearPreviousValues) {
            this.clearSort(false);
        }
    }

    /**
     * ** Update Browser URL either with predefined strategy or with one time update strategy provided as parameter.
     *
     *      - Updates are debounced by default.
     *      - optionally: debounce could be skipped and Browser URL would be updated immediately if 2nd parameter is provided with false value.
     */
    updateBrowserUrl(updateStrategy?: 'navigateToUrl' | 'locationToURL' | 'replaceToURL', skipDebouncing = false): void {
        const strategy = CollectionsUtil.isStringWithContent(updateStrategy) ? updateStrategy : this._updateStrategy;

        this.cancelScheduledBrowserUrlUpdate();

        if (skipDebouncing) {
            this._doUpdateBrowserUrl(strategy);

            return;
        }

        // debouncing for update URL, to avoid multiple updates when there are multiple serial near close update events
        this._updateTimeoutRef = setTimeout(() => {
            this._doUpdateBrowserUrl(strategy);
        }, this._debouncingTime);
    }

    /**
     * ** Cancel scheduled (debounced) Browser URL update.
     *
     *      - if canceled it won't update until next change occurs or {@link updateBrowserUrl} method is invoked on demand.
     */
    cancelScheduledBrowserUrlUpdate(): void {
        if (CollectionsUtil.isNumber(this._updateTimeoutRef)) {
            clearTimeout(this._updateTimeoutRef);
        }
    }

    /**
     * ** Change Manager Base url.
     *
     *      - it will update {@link URLStateManager} base url.
     */
    changeBaseUrl(baseUrl: string): void {
        this.urlStateManager.changeBaseUrl(baseUrl);
    }

    /**
     * ** Change Manager default update strategy.
     */
    changeUpdateStrategy(strategy: 'navigateToUrl' | 'locationToURL' | 'replaceToURL'): void {
        this._updateStrategy = strategy;
    }

    /**
     * ** Change Manager default debouncing time.
     */
    changeDebouncingTime(debouncingTime: number): void {
        if (!CollectionsUtil.isNumber(debouncingTime) || CollectionsUtil.isNaN(debouncingTime)) {
            return;
        }

        this._debouncingTime = debouncingTime;
    }

    /**
     * ** Register mutation observer, that will be invoked whenever mutation occurs in manager, either filter or sort mutation.
     */
    registerMutationObserver(callback: FilterSortMutationObserver<FC, FV, SC, SV>): void {
        if (this._mutationObservers.has(callback)) {
            return;
        }

        this._mutationObservers.add(callback);
    }

    /**
     * ** Delete mutation observer.
     */
    deleteMutationObserver(callback: FilterSortMutationObserver<FC, FV, SC, SV>): boolean {
        if (!this._mutationObservers.has(callback)) {
            return false;
        }

        this._mutationObservers.delete(callback);

        return true;
    }

    /**
     * ** Persist filter tuple pairs of key-value in filter storage {@link filterCriteria}.
     * @private
     */
    private _persistBulkFilters(filterPairs: KeyValueTuple<FC, FV>[], clearPreviousValues: boolean): KeyValueTuple<FC, FV>[] {
        const mutatedFilterPairs: KeyValueTuple<FC, FV>[] = [];

        for (const knownCriteria of this.knownFilterCriteria) {
            const foundFilterPairs = filterPairs.filter(([criteria, _value, type]) => criteria === knownCriteria && type === 'filter');

            if (foundFilterPairs.length > 0) {
                const value = foundFilterPairs.pop()[1];

                if (CollectionsUtil.isDefined(value)) {
                    if (this.filterCriteria[knownCriteria] !== value) {
                        this.filterCriteria[knownCriteria] = value;

                        mutatedFilterPairs.push([knownCriteria, value, 'filter']);
                    }
                } else if (this.hasFilter(knownCriteria)) {
                    delete this.filterCriteria[knownCriteria];

                    mutatedFilterPairs.push([knownCriteria, null, 'filter']);
                }
            } else if (clearPreviousValues) {
                if (this.hasFilter(knownCriteria)) {
                    delete this.filterCriteria[knownCriteria];

                    mutatedFilterPairs.push([knownCriteria, null, 'filter']);
                }
            }
        }

        return mutatedFilterPairs;
    }

    /**
     * ** Persist sort tuple pairs of key-value in sort storage {@link sortCriteria}.
     * @private
     */
    private _persistBulkSort(sortPairs: KeyValueTuple<SC, SV>[], clearPreviousValues: boolean): KeyValueTuple<SC, SV>[] {
        const mutatedSortPairs: KeyValueTuple<SC, SV>[] = [];

        for (const knownCriteria of this.knownSortCriteria) {
            const foundSortPairs = sortPairs.filter(([criteria, _direction, type]) => criteria === knownCriteria && type === 'sort');

            if (foundSortPairs.length > 0) {
                const value = foundSortPairs.pop()[1];

                if (CollectionsUtil.isDefined(value)) {
                    let normalizedValue: SV;

                    if (CollectionsUtil.isString(value)) {
                        if (/^(-)?\d+$/.test(value)) {
                            normalizedValue = parseInt(value, 10) as SV;
                        } else if (CollectionsUtil.isStringWithContent(value)) {
                            normalizedValue = value;
                        } else {
                            normalizedValue = null;
                        }
                    } else {
                        normalizedValue = value;
                    }

                    if (CollectionsUtil.isDefined(normalizedValue)) {
                        if (this.sortCriteria[knownCriteria] !== normalizedValue) {
                            this.sortCriteria[knownCriteria] = normalizedValue;

                            mutatedSortPairs.push([knownCriteria, normalizedValue, 'sort']);
                        }
                    } else if (this.hasSort(knownCriteria)) {
                        delete this.sortCriteria[knownCriteria];

                        mutatedSortPairs.push([knownCriteria, null, 'sort']);
                    }
                } else if (this.hasSort(knownCriteria)) {
                    delete this.sortCriteria[knownCriteria];

                    mutatedSortPairs.push([knownCriteria, null, 'sort']);
                }
            } else if (clearPreviousValues) {
                if (this.hasSort(knownCriteria)) {
                    delete this.sortCriteria[knownCriteria];

                    mutatedSortPairs.push([knownCriteria, null, 'sort']);
                }
            }
        }

        return mutatedSortPairs;
    }

    /**
     * ** Serialize filters for query params.
     * @private
     */
    private _serializeFilters(): void {
        const filterPairs = CollectionsUtil.objectPairs(this.filterCriteria);
        const normalizedFilterPairs: string = filterPairs.length > 0 ? JSON.stringify(this.filterCriteria) : null;

        this._updateUrlStateManager([FILTER_KEY, normalizedFilterPairs]);
    }

    private _deserializeFilters(value: string): Record<FC, FV> {
        try {
            return JSON.parse(value) as Record<FC, FV>;
        } catch (error) {
            console.error(`FiltersManager: Failed to parse Filters`, error);

            return {} as Record<FC, FV>;
        }
    }

    /**
     * ** Serialize sort for query params.
     * @private
     */
    private _serializeSort(): void {
        const sortPairs = CollectionsUtil.objectPairs(this.sortCriteria);
        const normalizedSortPairs: string = sortPairs.length > 0 ? JSON.stringify(this.sortCriteria) : null;

        this._updateUrlStateManager([SORT_KEY, normalizedSortPairs]);
    }

    private _deserializeSort(value: string): Record<SC, SV> {
        try {
            return JSON.parse(value) as Record<SC, SV>;
        } catch (error) {
            console.error(`FiltersManager: Failed to parse Sort`, error);

            return {} as Record<SC, SV>;
        }
    }

    /**
     * ** Actual update for Browser URL through {@link URLStateManager}.
     * @private
     */
    private _doUpdateBrowserUrl(strategy: 'navigateToUrl' | 'locationToURL' | 'replaceToURL'): void {
        if (strategy === 'locationToURL') {
            this.urlStateManager.locationToURL();
        } else if (strategy === 'replaceToURL') {
            this.urlStateManager.replaceToUrl();
        } else {
            this.urlStateManager
                .navigateToUrl()
                .then(() => {
                    // No-op.
                })
                .catch((error) => {
                    console.error(`FiltersManager: Failed to update Browser Url`, error);
                });
        }
    }

    /**
     * ** Update {@link URLStateManager} query params using provided key-value tuples.
     * @private
     */
    private _updateUrlStateManager(...updatePairs: KeyValueTuple<typeof FILTER_KEY | typeof SORT_KEY, string>[]): void {
        for (const [criteria, value] of updatePairs) {
            this.urlStateManager.setQueryParam(criteria, value);
        }
    }

    /**
     * ** Notify mutation observers providing Array of tuples for mutated key-value.
     * @private
     */
    private _notifyMutationObservers(changes: KeyValueTuple<FC | SC, FV | SV>[]): void {
        if (changes.length === 0) {
            return;
        }

        this._mutationObservers.forEach((observer) => {
            try {
                observer(changes);
            } catch (error) {
                console.error(`FiltersManager: Failed to notify mutation observers`, error);
            }
        });
    }
}
