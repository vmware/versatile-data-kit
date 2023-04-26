/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, ViewChild, ViewContainerRef } from '@angular/core';

/**
 * ** Dynamic Container Component is created only once upon {@link DynamicComponentsService} initialization
 *      and is container for all contextually created ViewContainerRef instances for every single UUID.
 *
 *      - It is created only once, and its populated field {@link DynamicContainerComponent.viewContainerRef}
 *              is stored as ViewContainerRef in {@link DynamicComponentsService} for lifetime of the service as singleton.
 */
@Component({
    selector: 'shared-dynamic-components-container',
    templateUrl: './dynamic-container.component.html',
    styleUrls: ['./dynamic-container.component.scss']
})
export class DynamicContainerComponent {
    /**
     * ** ViewContainerRef reference that is used as point where {@link DynamicComponentsService} insert contextual {@link DynamicContextComponent}
     *      one for every single UUID when invokers call {@link DynamicComponentsService.getUniqueViewContainerRef}.
     *
     *      - Reference is singleton, and it is retrieved only once upon {@link DynamicComponentsService} initialization.
     */
    @ViewChild('dynamicComponentsContainer', { read: ViewContainerRef, static: true })
    public readonly viewContainerRef: ViewContainerRef;
}
