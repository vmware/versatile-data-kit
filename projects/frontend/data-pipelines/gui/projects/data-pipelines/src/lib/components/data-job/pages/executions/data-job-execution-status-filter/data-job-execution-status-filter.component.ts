/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';

import { Observable, Subject } from 'rxjs';

import { ClrDatagridFilterInterface } from '@clr/angular';

import { CollectionsUtil } from '@versatiledatakit/shared';

import { DataJobExecutionStatus } from '../../../../../model';

import { GridDataJobExecution } from '../model';

@Component({
    selector: 'lib-data-job-execution-status-filter',
    templateUrl: './data-job-execution-status-filter.component.html'
})
export class DataJobExecutionStatusFilterComponent implements OnChanges, ClrDatagridFilterInterface<GridDataJobExecution> {
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

    allStatuses = [
        DataJobExecutionStatus.SUCCEEDED,
        DataJobExecutionStatus.PLATFORM_ERROR,
        DataJobExecutionStatus.USER_ERROR,
        DataJobExecutionStatus.RUNNING,
        DataJobExecutionStatus.SUBMITTED,
        DataJobExecutionStatus.SKIPPED,
        DataJobExecutionStatus.CANCELLED
    ];

    selectedStatuses: string[] = [];

    // We do not want to expose the Subject itself, but the Observable which is read-only
    get changes(): Observable<string> {
        return this._changesSubject.asObservable();
    }

    private _changesSubject = new Subject<string>();

    isActive(): boolean {
        return this.selectedStatuses.length > 0;
    }

    accepts(item: GridDataJobExecution): boolean {
        return this.selectedStatuses.indexOf(item.status) > -1;
    }

    toggleCheckbox($event: Event) {
        const checkbox = $event.target as HTMLInputElement;

        if (checkbox.checked) {
            this.selectedStatuses.push(checkbox.value);
        } else {
            const statusToRemoveIndex = this.selectedStatuses.indexOf(checkbox.value);
            if (statusToRemoveIndex > -1) {
                this.selectedStatuses.splice(statusToRemoveIndex, 1);
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
            const checkedValues = this._deserializeStatuses();
            for (const checkedValue of checkedValues) {
                if (this.allStatuses.includes(checkedValue)) {
                    selectedTypes.push(checkedValue);
                }
            }
        }

        this.selectedStatuses = selectedTypes;

        this._updateValue();
    }

    private _updateValue(notifyChange = false): void {
        const serializedValue = this._serializeStatuses();

        this.value = serializedValue;
        this._changesSubject.next(serializedValue);

        if (notifyChange) {
            this.valueChange.next(serializedValue);
        }
    }

    private _serializeStatuses(): string {
        return this.selectedStatuses.join(',').toLowerCase();
    }

    private _deserializeStatuses(): DataJobExecutionStatus[] {
        return this.value.toUpperCase().split(',') as DataJobExecutionStatus[];
    }
}
