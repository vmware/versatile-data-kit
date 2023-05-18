/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';

import { Observable, Subject } from 'rxjs';

import { ClrDatagridFilterInterface } from '@clr/angular';

import { CollectionsUtil } from '@versatiledatakit/shared';

import { DataJobExecutionType } from '../../../../../model';

import { GridDataJobExecution } from '../model/data-job-execution';

@Component({
    selector: 'lib-data-job-execution-type-filter',
    templateUrl: './data-job-execution-type-filter.component.html'
})
export class DataJobExecutionTypeFilterComponent implements OnChanges, ClrDatagridFilterInterface<GridDataJobExecution> {
    /**
     * ** Path to value (property).
     */
    @Input() property: string;

    /**
     * ** Value bound to {@link property}.
     */
    @Input() value: string;

    /**
     * ** Event emitter that emits whenever {@link value} change.
     */
    @Output() valueChange = new EventEmitter<string>();

    allTypes = [DataJobExecutionType.MANUAL, DataJobExecutionType.SCHEDULED];
    selectedTypes: string[] = [];

    // We do not want to expose the Subject itself, but the Observable which is read-only
    get changes(): Observable<string> {
        return this._changesSubject.asObservable();
    }

    private _changesSubject = new Subject<string>();

    isActive(): boolean {
        return this.selectedTypes.length > 0;
    }

    accepts(item: GridDataJobExecution): boolean {
        return this.selectedTypes.indexOf(item.type) > -1;
    }

    toggleCheckbox(event: Event) {
        const checkbox = event.target as HTMLInputElement;

        if (checkbox.checked) {
            this.selectedTypes.push(checkbox.value);
        } else {
            const statusToRemoveIndex = this.selectedTypes.indexOf(checkbox.value);
            if (statusToRemoveIndex > -1) {
                this.selectedTypes.splice(statusToRemoveIndex, 1);
            }
        }

        this._updateValue(true);
    }

    /**
     * @inheritDoc
     */
    ngOnChanges(changes: SimpleChanges): void {
        if (changes['value']) {
            this._refreshValue();
        }
    }

    private _refreshValue(): void {
        const selectedTypes: string[] = [];

        if (CollectionsUtil.isStringWithContent(this.value)) {
            const checkedValues = this._deserializeTypes();
            for (const checkedValue of checkedValues) {
                if (this.allTypes.includes(checkedValue)) {
                    selectedTypes.push(checkedValue);
                }
            }
        }

        this.selectedTypes = selectedTypes;

        this._updateValue();
    }

    private _updateValue(notifyChange = false): void {
        const serializedValue = this._serializeTypes();

        this.value = serializedValue;
        this._changesSubject.next(serializedValue);

        if (notifyChange) {
            this.valueChange.next(serializedValue);
        }
    }

    private _serializeTypes(): string {
        return this.selectedTypes.join(',').toLowerCase();
    }

    private _deserializeTypes(): DataJobExecutionType[] {
        return this.value.toUpperCase().split(',') as DataJobExecutionType[];
    }
}
