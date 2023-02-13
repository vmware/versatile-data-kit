/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';

import { DataJob } from '../../../model';

@Component({
    selector: 'lib-widget-execution-status-gauge',
    templateUrl: './widget-execution-status-gauge.component.html',
    styleUrls: ['./widget-execution-status-gauge.component.scss']
})
export class WidgetExecutionStatusGaugeComponent implements OnChanges {

    @Input() allJobs: DataJob[];
    failedExecutions: number;
    successfulExecutions: number;
    totalExecutions: number;
    successRate: number;
    loading = true;

    ngOnChanges(changes: SimpleChanges) {
        if (changes['allJobs'].currentValue) {
            this.failedExecutions = 0;
            this.successfulExecutions = 0;
            (changes['allJobs'].currentValue as DataJob[]).forEach(
                (dataJob) => {
                    if (dataJob.deployments) {
                        this.failedExecutions += dataJob.deployments[0].failedExecutions;
                        this.successfulExecutions += dataJob.deployments[0].successfulExecutions;
                    }
                }
            );
            this.totalExecutions = this.failedExecutions + this.successfulExecutions;
            this.successRate = this.successfulExecutions / this.totalExecutions;
            this.loading = false;
        }
    }

    customColors(name) {
        if (name >= 95) {
            return '#5AA220';
        } else if (name >= 90) {
            return '#EFC006';
        } else {
            return '#F35E44';
        }
    }
}
