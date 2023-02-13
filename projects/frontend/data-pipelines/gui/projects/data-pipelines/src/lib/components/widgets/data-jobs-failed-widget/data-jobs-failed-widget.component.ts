/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ChangeDetectionStrategy, Component, Input, OnChanges, SimpleChanges } from '@angular/core';

import { NavigationService } from '@vdk/shared';

import { DataJob, DataJobExecutions } from '../../../model';

interface DataJobGrid extends DataJob {
    failedTotal?: number;
}

@Component({
    selector: 'lib-data-jobs-failed-widget',
    templateUrl: './data-jobs-failed-widget.component.html',
    styleUrls: ['./data-jobs-failed-widget.component.scss'],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DataJobsFailedWidgetComponent implements OnChanges {

    @Input() manageLink: string;
    @Input() allJobs: DataJob[];
    @Input() jobExecutions: DataJobExecutions = [];

    readonly uuid = 'DataJobsFailedWidgetComponent';

    loading = true;
    dataJobs: DataJobGrid[] = [];

    constructor(private readonly navigationService: NavigationService) {
    }

    /**
     * ** NgFor elements tracking function.
     */
    trackByFn(index: number, dataJob: DataJob): string {
        return `${ index }|${ dataJob?.jobName }`;
    }

    /**
     * @inheritDoc
     */
    ngOnChanges(changes: SimpleChanges) {
        if (changes['jobExecutions'] !== undefined) {
            this.dataJobs = [];
            (changes['jobExecutions'].currentValue as DataJobExecutions).forEach((element) => {
                const temp = this.dataJobs.find(i => i.jobName === element.jobName);
                if (!temp) {
                    this.dataJobs.push({ jobName: element.jobName, failedTotal: 1 } as DataJobGrid);
                } else {
                    temp.failedTotal++;
                }
            });
            this.loading = false;
        }
    }

    navigateToJobDetails(job?: DataJob): void {
        const dataJob = this.allJobs.find(el => el.jobName === job.jobName);
        let link = this.manageLink;
        link = link.replace('{team}', dataJob.config?.team);
        link = link.replace('{data-job}', job.jobName);
        link = link + '/details';

        if (dataJob) {
            // eslint-disable-next-line @typescript-eslint/no-floating-promises
            this.navigationService.navigate(link);
        }
    }
}
