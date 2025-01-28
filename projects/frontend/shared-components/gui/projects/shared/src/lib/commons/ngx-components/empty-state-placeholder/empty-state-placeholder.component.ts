/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/* eslint-disable */

import { Component, Input } from '@angular/core';

@Component({
    selector: 'vdk-empty-state-placeholder',
    templateUrl: './empty-state-placeholder.component.html',
    styleUrls: ['./empty-state-placeholder.component.scss']
})
export class VdkEmptyStatePlaceholderComponent {
    @Input('title') title: string;
    @Input() icon: string;
    @Input() description: string;
    @Input() headingLevel = 2;
}
