/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, HostListener, Input } from '@angular/core';

import { DataJobExecutionStatus } from '../../../../../model';

type StatusPropertiesMapping = { shape: string; status: string; direction: string; text: string };

@Component({
    selector: 'lib-data-job-execution-status',
    templateUrl: './data-job-execution-status.component.html',
    styleUrls: ['./data-job-execution-status.component.scss']
})
export class DataJobExecutionStatusComponent {

    @HostListener('mouseenter') onMouseEnter(): void {
        this.clrOpen = true;
    }

    @HostListener('mouseleave') onMouseLeave(): void {
        this.clrOpen = false;
    }

    @Input() jobStatus: DataJobExecutionStatus;
    @Input() jobMessage = '';
    @Input() showErrorMessage = false;
    clrOpen = false;

    statusPropertiesMapping: { [key: string]: StatusPropertiesMapping } = {
        [DataJobExecutionStatus.SUBMITTED]: { shape: 'hourglass', status: '', direction: '', text: 'Submitted' },
        [DataJobExecutionStatus.RUNNING]: { shape: 'play', status: '', direction: '', text: 'Running' },
        [DataJobExecutionStatus.SUCCEEDED]: { shape: 'success-standard', status: 'is-success', direction: '', text: 'Success' },
        [DataJobExecutionStatus.CANCELLED]: { shape: 'ban', status: '', direction: '', text: 'Canceled' },
        [DataJobExecutionStatus.SKIPPED]: { shape: 'angle-double', status: '', direction: 'right', text: 'Skipped' },
        [DataJobExecutionStatus.USER_ERROR]: { shape: 'error-standard', status: 'is-danger', direction: '', text: 'User Error' },
        [DataJobExecutionStatus.PLATFORM_ERROR]: { shape: 'error-standard', status: 'is-warning', direction: '', text: 'Platform Error' },
        [DataJobExecutionStatus.FAILED]: { shape: 'error-standard', status: 'is-danger', direction: '', text: 'Error' }
    };

    get executionStatusProperties(): StatusPropertiesMapping {
        return this.statusPropertiesMapping[this.jobStatus] ?? {} as StatusPropertiesMapping;
    }

    isJobStatusSuitableForMessageTooltip(): boolean {
        return this.jobStatus === DataJobExecutionStatus.PLATFORM_ERROR || this.jobStatus === DataJobExecutionStatus.USER_ERROR || this.jobStatus === DataJobExecutionStatus.SKIPPED;
    }

    isJobMessageDifferentFromStatus(): boolean {
        const message = this.jobMessage?.toLowerCase();
        return message !== 'user error' && message !== 'platform error' && message !== 'skipped' && message !== '';
    }
}
