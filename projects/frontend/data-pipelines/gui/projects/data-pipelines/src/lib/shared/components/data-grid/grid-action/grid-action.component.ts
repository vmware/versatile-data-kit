/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
    AfterViewInit,
    Component,
    EventEmitter,
    Input,
    OnChanges,
    Output,
    SimpleChanges,
    ViewEncapsulation,
} from '@angular/core';

import { CollectionsUtil } from '@vdk/shared';

import { QuickFilterChangeEvent, QuickFilters } from '../../quick-filters';

@Component({
    selector: 'lib-grid-action',
    templateUrl: './grid-action.component.html',
    styleUrls: ['./grid-action.component.scss'],
    encapsulation: ViewEncapsulation.None,
})
export class GridActionComponent implements AfterViewInit, OnChanges {
    @Input() id = 'lib-ga-search-id';
    @Input() addId = 'lib-ga-add-id';
    @Input() editId = 'lib-ga-edit-id';
    @Input() removeId = 'lib-ga-remove-id';

    @Input() addLabel: string;
    @Input() editLabel: string;
    @Input() removeLabel: string;

    @Input() addTooltip: string;
    @Input() editTooltip: string;
    @Input() removeTooltip: string;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    @Input() selectedValue: any | any[];
    @Input() searchQueryValue = '';

    @Input() disableAdd: boolean;
    @Input() disableEdit: boolean;
    @Input() disableRemove: boolean;

    /**
     * ** Proxy config for QuickFilters component.
     */
    @Input() quickFilters: QuickFilters;
    @Input() suppressQuickFilterChangeEvent: boolean;

    /**
     * ** Proxy emitter from QuickFilters component.
     */
    @Output() quickFilterChange = new EventEmitter<QuickFilterChangeEvent>();

    @Output() search: EventEmitter<string> = new EventEmitter<string>();
    @Output() add: EventEmitter<boolean> = new EventEmitter<boolean>();
    /* eslint-disable @typescript-eslint/no-explicit-any */
    @Output() edit: EventEmitter<any> = new EventEmitter<any>();
    @Output() remove: EventEmitter<any> = new EventEmitter<any>();
    /* eslint-enable @typescript-eslint/no-explicit-any */

    queryValue: string;

    ngAfterViewInit(): void {
        this.setQueryValue();
    }

    ngOnChanges(changes: SimpleChanges): void {
        if (changes['searchQueryValue']) {
            this.setQueryValue();
        }
    }

    get editDisabled(): boolean {
        return (
            CollectionsUtil.isNil(this.selectedValue) ||
            (CollectionsUtil.isString(this.selectedValue) &&
                this.selectedValue.length === 0) ||
            this.disableEdit
        );
    }

    get addDisabled(): boolean {
        return this.disableAdd;
    }

    get removeDisabled(): boolean {
        return (
            CollectionsUtil.isNil(this.selectedValue) ||
            (CollectionsUtil.isString(this.selectedValue) &&
                this.selectedValue.length === 0) ||
            this.disableRemove
        );
    }

    /**
     * vmw-search is being broken for one-way binding related to an input [searchQueryValue]
     * this fix is a workaround (adding a delay of 1 milisecond to set queryValue, looks like
     * needs to run in a separate thread)
     */
    private setQueryValue() {
        setTimeout(() => {
            this.queryValue = this.searchQueryValue;
        }, 1);
    }
}
