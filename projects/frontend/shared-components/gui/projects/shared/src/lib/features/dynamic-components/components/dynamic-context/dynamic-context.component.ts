/*
 * Copyright 2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, ViewChild, ViewContainerRef } from '@angular/core';

/**
 * ** Dynamic Context Component that is created for every UUID in {@link DynamicComponentsService}.
 *
 *      - It is created multiple times, once for every single UUID, and its populated field {@link DynamicContextComponent.viewContainerRef}
 *              is stored as ViewContainerRef in {@link DynamicComponentsService} that is returned to the invoker,
 *              to meet their needs for creating dynamic Components.
 */
@Component({
    selector: 'shared-dynamic-components-context',
    templateUrl: './dynamic-context.component.html',
    styleUrls: ['./dynamic-context.component.scss']
})
export class DynamicContextComponent {
    /**
     * ** ViewContainerRef reference that is used as point where invokers of {@link DynamicComponentsService.getUniqueViewContainerRef}
     *      retrieve reference of, and could insert their Components.
     *
     *      - Reference is totally contextual and unique for every single UUID and other invokers won't be bothered.
     */
    @ViewChild('dynamicComponentsContext', { read: ViewContainerRef, static: true })
    public readonly viewContainerRef: ViewContainerRef;
}
