/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';

import { Subject } from 'rxjs';

import { ClrDatagridFilterInterface } from '@clr/angular';

import { DataJobExecutionStatus } from '../../../../../model';

import { GridDataJobExecution } from '../model';

@Component({
    selector: 'lib-data-job-execution-status-filter',
    templateUrl: './data-job-execution-status-filter.component.html'
})
export class DataJobExecutionStatusFilterComponent implements ClrDatagridFilterInterface<GridDataJobExecution> {

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

    changes: Subject<boolean> = new Subject<boolean>();

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

        this.changes.next(true);
    }
}
