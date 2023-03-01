/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input } from '@angular/core';

import { DataJobDeployment } from '../../../../model';

@Component({
    selector: 'lib-status-panel',
    templateUrl: './status-panel.component.html',
    styleUrls: ['./status-panel.component.css'],
})
export class StatusPanelComponent {
    @Input() jobDeployments: DataJobDeployment[];
}
