/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';

import { Subject } from 'rxjs';

import { ClrDatagridFilterInterface } from '@clr/angular';

import { DataJobExecutionType } from '../../../../../model';

import { GridDataJobExecution } from '../model/data-job-execution';

@Component({
    selector: 'lib-data-job-execution-type-filter',
    templateUrl: './data-job-execution-type-filter.component.html',
})
export class DataJobExecutionTypeFilterComponent
    implements ClrDatagridFilterInterface<GridDataJobExecution>
{
    allTypes = [DataJobExecutionType.MANUAL, DataJobExecutionType.SCHEDULED];
    selectedTypes: string[] = [];
    changes: Subject<boolean> = new Subject<boolean>();

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
            const statusToRemoveIndex = this.selectedTypes.indexOf(
                checkbox.value
            );
            if (statusToRemoveIndex > -1) {
                this.selectedTypes.splice(statusToRemoveIndex, 1);
            }
        }

        this.changes.next(true);
    }
}
