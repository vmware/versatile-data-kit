/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { HostBinding, Input, Component } from '@angular/core';
import {
    trigger,
    transition,
    query,
    animateChild,
    stagger,
} from '@angular/animations';

import {
    multiply,
    STAGGER_DURATION,
} from "../animation-constants";

import { VdkToastComponent } from './toast.component';

@Component({
    selector: "vdk-toast-container",
    templateUrl: "./toast-container.component.html",
    styleUrls: ["./toast-container.component.scss"],
    animations:[
        trigger('toastContainer', [
            transition(':enter', [
                query('@launchToast', [
                    stagger(`${multiply(STAGGER_DURATION)}ms`, animateChild())
                ], {optional: true}),
            ]),
            transition(':leave', [
                query('@launchToast', [
                    animateChild()
                ], {optional:true})
            ]),
        ])
    ]
})
export class VdkToastContainerComponent {
    @Input() topOffset: number = 0;

    @HostBinding('style.top')
    get top(): string {
        return (60 + this.topOffset) + 'px';
    }
}
