/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/** @format */

import { Component, Input } from '@angular/core';

@Component({
    selector: 'lib-empty-state',
    templateUrl: './empty-state.component.html',
    styleUrls: ['./empty-state.component.scss'],
})
export class EmptyStateComponent {
    @Input() title = 'Empty State';
    @Input() description = 'Description';
    @Input() width = 256;
    @Input() imgSrc: string;
    @Input() hideImage = false;
    @Input() opacity = 1;
    @Input() animSrc =
        'assets/animations/no-events-in-timeframe-animation.json';
    @Input() marginTop = '3rem';
    @Input() marginBottom = '20px';
}
