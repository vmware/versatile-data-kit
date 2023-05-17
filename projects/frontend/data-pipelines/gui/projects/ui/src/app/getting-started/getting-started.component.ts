/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { AppConfigService } from '../app-config.service';

@Component({
    selector: 'app-getting-started',
    templateUrl: './getting-started.component.html',
    styleUrls: ['./getting-started.component.scss']
})
export class GettingStartedComponent {
    constructor(private readonly appConfigService: AppConfigService) {
        // No-op.
    }

    get widgetsVisible(): boolean {
        return !this.appConfigService.getConfig().ignoreComponents.includes('widgetsComponent');
    }
}
