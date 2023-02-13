/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ChangeDetectionStrategy, ChangeDetectorRef, Component, Input } from '@angular/core';

import { ClrDatagridSortOrder } from '@clr/angular';

import { DataJobDeployment } from '../../../../../model';

import { GridDataJobExecution } from '../model';

import { DataJobExecutionDurationComparator } from './comparators/execution-duration-comparator';

@Component({
    selector: 'lib-data-job-executions-grid',
    templateUrl: './data-job-executions-grid.component.html',
    styleUrls: ['./data-job-executions-grid.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DataJobExecutionsGridComponent {

    @Input() jobExecutions: GridDataJobExecution[];
    @Input() loading = false;

    // Sorting
    descSort = ClrDatagridSortOrder.DESC;
    durationComparator = new DataJobExecutionDurationComparator();
    // End of sorting
    openDeploymentDetailsModal = false;
    jobDeploymentModalData: DataJobDeployment;

    /**
     * ** Constructor.
     */
    constructor(private readonly changeDetectorRef: ChangeDetectorRef) {
    }

    /**
     * ** NgFor elements tracking function.
     */
    trackByFn(index: number, execution: GridDataJobExecution): string {
        return `${ index }|${ execution?.id }`;
    }

    showDeploymentDetails(jobExecution: GridDataJobExecution) {
        this.openDeploymentDetailsModal = true;
        this.jobDeploymentModalData = jobExecution.deployment;

        this.changeDetectorRef.detectChanges();
    }
}
