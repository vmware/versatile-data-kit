/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ChangeDetectionStrategy, Component, Input, OnChanges, SimpleChanges } from '@angular/core';

import { NavigationService } from '@versatiledatakit/shared';

import { DataJob, DataJobExecution } from '../../../model';

import { GridDataJobExecution } from '../../data-job/pages/executions';

@Component({
    selector: 'lib-data-jobs-executions-widget',
    templateUrl: './data-jobs-executions-widget.component.html',
    styleUrls: ['./data-jobs-executions-widget.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DataJobsExecutionsWidgetComponent implements OnChanges {
    @Input() manageLink: string;
    @Input() allJobs: DataJob[];
    @Input() jobExecutions: GridDataJobExecution[] = [];

    readonly uuid = 'DataJobsExecutionsWidgetComponent';

    loading = true;

    constructor(private readonly navigationService: NavigationService) {}

    /**
     * ** NgFor elements tracking function.
     */
    trackByFn(index: number, execution: DataJobExecution): string {
        return `${index}|${execution?.id}`;
    }

    /**
     * @inheritDoc
     */
    ngOnChanges(changes: SimpleChanges) {
        if (changes['jobExecutions'] !== undefined && changes['jobExecutions'].currentValue !== undefined) {
            this.loading = false;
        }
    }

    navigateToJobExecutions(job?: DataJobExecution): void {
        const dataJob = this.allJobs.find((el) => el.jobName === job.jobName);
        let link = this.manageLink;
        link = link.replace('{team}', dataJob.config?.team);
        link = link.replace('{data-job}', dataJob.jobName);
        link = link + '/executions';

        if (dataJob) {
            // eslint-disable-next-line @typescript-eslint/no-floating-promises
            this.navigationService.navigate(link);
        }
    }
}
