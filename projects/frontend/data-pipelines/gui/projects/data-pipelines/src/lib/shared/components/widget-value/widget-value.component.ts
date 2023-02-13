/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { Observable } from 'rxjs';

@Component({
    selector: 'lib-widget-value',
    templateUrl: './widget-value.component.html',
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class WidgetValueComponent {
    @Input() observable$: Observable<unknown>;
    @Input() prop: string;
    @Input() showErrorState: boolean;
}
