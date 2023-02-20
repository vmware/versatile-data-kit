/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input } from '@angular/core';

import { DataJobExecutionType } from '../../../../../model';

import { GridDataJobExecution } from '../model/data-job-execution';

@Component({
    selector: 'lib-data-job-execution-type',
    templateUrl: './data-job-execution-type.component.html'
})
export class DataJobExecutionTypeComponent {

    @Input() jobExecution: GridDataJobExecution;

    executionTypePropertiesMapping = {
        [DataJobExecutionType.MANUAL]: { shape: 'cursor-hand-open', status: 'is-info' },
        [DataJobExecutionType.SCHEDULED]: { shape: 'clock', status: '' }
    };

    get executionTypeProperties() {
        return this.executionTypePropertiesMapping[this.jobExecution.type];
    }
}
