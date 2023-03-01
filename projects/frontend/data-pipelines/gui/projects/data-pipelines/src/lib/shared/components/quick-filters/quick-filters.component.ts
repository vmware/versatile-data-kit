/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
    Component,
    EventEmitter,
    Input,
    OnChanges,
    Output,
    SimpleChanges,
} from '@angular/core';

import { CollectionsUtil } from '@vdk/shared';

import { QuickFilter, QuickFilterChangeEvent, QuickFilters } from './model';

@Component({
    selector: 'lib-quick-filters',
    templateUrl: './quick-filters.component.html',
    styleUrls: ['./quick-filters.component.scss'],
})
export class QuickFiltersComponent implements OnChanges {
    /**
     * ** Quick Filters array config.
     */
    @Input() set quickFilters(filters: QuickFilters) {
        this._quickFilters = CollectionsUtil.isArray(filters) ? filters : [];
    }

    get quickFilters(): QuickFilters {
        return this._quickFilters;
    }

    /**
     * ** Show or hide Label "QUICK FILTERS" before filters list.
     *
     *  - true  - Show
     *  - false - Hide
     */
    @Input() showFiltersLabel = false;

    /**
     * ** Suppress emitted event when some filter state change.
     *
     *  - true  - Event wont be emitted
     *  - false - Event would be emitted on change
     */
    @Input() suppressQuickFilterChangeEvent = false;

    /**
     * ** Event Emitter for Filter state change.
     */
    @Output() quickFilterChange = new EventEmitter<QuickFilterChangeEvent>();

    activatedFilter: QuickFilter;

    private _quickFilters: QuickFilters = [];
    private _deactivatedFilter: QuickFilter | null = null;

    /**
     * ** NgFor elements tracking function.
     */
    trackByFn(index: number, filter: QuickFilter): string {
        return `${index}|${filter.id}`;
    }

    /**
     * ** Executed when some filter change it's state.
     * <p>
     *     State changes when User click on some Filter or press Enter while it's on focus.
     * </p>
     */
    changeFilter(filter: QuickFilter): void {
        const executeOnDeactivate = (dFilter: QuickFilter) => {
            if (
                this.suppressQuickFilterChangeEvent &&
                CollectionsUtil.isDefined(dFilter) &&
                CollectionsUtil.isFunction(dFilter.onDeactivate)
            ) {
                dFilter.onDeactivate();
            }
        };

        if (this.activatedFilter === filter) {
            if (!filter.suppressCancel) {
                this._deactivatedFilter = this.activatedFilter;
                this.activatedFilter = null;
                executeOnDeactivate(this._deactivatedFilter);
            }
        } else {
            this._deactivatedFilter = this.activatedFilter;
            this.activatedFilter = filter;
            executeOnDeactivate(this._deactivatedFilter);
        }

        if (this.suppressQuickFilterChangeEvent) {
            if (
                CollectionsUtil.isDefined(this.activatedFilter) &&
                CollectionsUtil.isFunction(this.activatedFilter.onActivate)
            ) {
                this.activatedFilter.onActivate();
            } else {
                console.warn(
                    'QuickFiltersComponent: No listener for onActivate callback while Event Emitter is suppressed.'
                );
            }
        } else {
            this.quickFilterChange.emit({
                activatedFilter: this.activatedFilter,
                deactivatedFilter: this._deactivatedFilter,
            });
        }
    }

    /**
     * @inheritDoc
     */
    ngOnChanges(changes: SimpleChanges) {
        if (changes['quickFilters']) {
            if (!changes['quickFilters'].firstChange) {
                return;
            }

            const defaultActiveFilter = this.quickFilters.find((f) => f.active);

            if (CollectionsUtil.isDefined(defaultActiveFilter)) {
                this.activatedFilter = defaultActiveFilter;
            }
        }
    }
}
