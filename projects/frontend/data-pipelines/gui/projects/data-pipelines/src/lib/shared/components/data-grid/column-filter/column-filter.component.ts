/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, TemplateRef, ViewEncapsulation } from '@angular/core';

import { Observable, Subject } from 'rxjs';

import { ClrDatagridFilter, ClrDatagridFilterInterface } from '@clr/angular';

import { DataJob } from '../../../../model';

@Component({
    selector: 'lib-column-filter',
    templateUrl: './column-filter.component.html',
    styleUrls: ['./column-filter.component.scss'],
    encapsulation: ViewEncapsulation.None
})
export class ColumnFilterComponent implements ClrDatagridFilterInterface<DataJob>, OnChanges {
    @Input() property: string;
    @Input() listOfOptions: string[];
    @Input() isExecutionStatus = false;

    @Input() optionRenderer: TemplateRef<HTMLElement> = null;

    @Input() set value(_value: string) {
        this._value = _value === 'all' ? null : _value;
    }
    get value(): string {
        return this._value;
    }
    @Output() valueChange = new EventEmitter<string>();

    // We do not want to expose the Subject itself, but the Observable which is read-only
    get changes(): Observable<string> {
        return this._changesSubject.asObservable();
    }

    private _value: string;
    private _changesSubject = new Subject<string>();

    constructor(private filterContainer: ClrDatagridFilter) {
        filterContainer.setFilter(this);
    }

    isActive(): boolean {
        return !!this.value;
    }

    accepts(_item: DataJob): boolean {
        return true;
    }

    toggleSelection($event: Event) {
        this._setValue(($event.target as HTMLInputElement).value);
    }

    cleanFilter() {
        this._setValue(null);
    }

    isValueSelected(value: string) {
        return this.value?.toLowerCase() === value?.toLowerCase().replace(' ', '_');
    }

    /**
     * @inheritDoc
     */
    ngOnChanges(changes: SimpleChanges): void {
        this._changesSubject.next(changes['value'].currentValue as string);
    }

    private _setValue(value: string): void {
        this.value = value;
        this.valueChange.emit(this.value);
        this._changesSubject.next(this.value);
    }
}
