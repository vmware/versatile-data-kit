/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, ContentChild, Input, TemplateRef } from '@angular/core';

@Component({
    selector: 'shared-empty-state',
    templateUrl: './empty-state.component.html',
    styleUrls: ['./empty-state.component.scss']
})
export class EmptyStateComponent {
    @ContentChild('customTemplate', { read: TemplateRef }) customTemplateRef: TemplateRef<never>;

    /**
     * ** Title for empty state Component.
     */
    @Input() title: string;

    /**
     * ** Icon for empty state Component.
     */
    @Input() icon: string;

    /**
     * ** Description for empty state Component.
     */
    @Input() description: string;

    /**
     * ** Title heading level for empty state Component.
     */
    @Input() headingLevel = 2;
}
