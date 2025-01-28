/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input } from '@angular/core';

import { DataJobDeployment } from '../../../../model';

@Component({
    selector: 'lib-status-panel',
    templateUrl: './status-panel.component.html',
    styleUrls: ['./status-panel.component.css']
})
export class StatusPanelComponent {
    @Input() jobDeployments: DataJobDeployment[];
}
