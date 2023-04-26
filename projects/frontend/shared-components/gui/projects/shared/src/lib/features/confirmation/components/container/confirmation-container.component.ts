/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, ViewChild, ViewContainerRef } from '@angular/core';

/**
 * ** Confirmation Container Component is created only once upon {@link ConfirmationService} initialization
 *      and is container for all contextually created ViewContainerRef instances for every single confirmation ask.
 *
 *      - It is created only once, and its populated field {@link ConfirmationContainerComponent.viewContainerRef}
 *              is stored as ViewContainerRef in {@link ConfirmationService} for lifetime of the service as singleton.
 */
@Component({
    selector: 'shared-confirmation-container',
    templateUrl: './confirmation-container.component.html',
    styleUrls: ['./confirmation-container.component.scss']
})
export class ConfirmationContainerComponent {
    /**
     * ** ViewContainerRef reference that is used as point where {@link ConfirmationService} insert contextual {@link ConfirmationComponent}
     *      one for every single confirmation ask when invokers call {@link ConfirmationService.confirm}.
     *
     *      - Reference is singleton, and it is retrieved only once upon {@link ConfirmationService} initialization.
     */
    @ViewChild('insertionPoint', { read: ViewContainerRef })
    public readonly viewContainerRef: ViewContainerRef;

    /**
     * ** Input parameter that instructs Component to open/close modal (visualize/hide) confirmation view/s.
     *
     *      - State is managed from {@link ConfirmationService}
     */
    @Input() open = false;
}
