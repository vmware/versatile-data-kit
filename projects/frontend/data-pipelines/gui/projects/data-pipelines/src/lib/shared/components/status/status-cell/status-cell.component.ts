/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input } from '@angular/core';
import { DataJob } from '../../../../model/data-job.model';

@Component({
    selector: 'lib-status-cell',
    templateUrl: './status-cell.component.html',
    styleUrls: ['./status-cell.component.css'],
})
export class StatusCellComponent {
    @Input() dataJob: DataJob;
}
