/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import {
    ElementRef,
    NgZone,
    Component,
    Input,
    Output,
    EventEmitter,
    HostListener,
    Optional
} from "@angular/core";
import {
    trigger,
    group,
    style,
    animate,
    transition,
    query,
    animateChild,
    keyframes,
} from '@angular/animations';

import { timer } from "rxjs";
import { take } from "rxjs/operators";

import { VmwToastType } from "./toast.model";
import { TRANSLATIONS } from './toast.l10n';
import { VdkSimpleTranslateService } from "../../ngx-utils";

import {
    multiply,
    componentPrimaryEnterCurve,
    componentPrimaryEnterTiming,
    componentPrimaryLeaveCurve,
    componentPrimaryLeaveTiming,
    linePrimaryEnterCurve,
    linePrimaryEnterTiming,
    linePrimaryEnterDelay,
    lineSecondaryEnterCurve,
    lineSecondaryEnterTiming,
    lineSecondaryEnterDelay,
    DISMISS_ICON_DELAY,
    DISMISS_ICON_DURATION,
    DISMISS_ICON_CURVE,
    GRADIENT_DURATION,
    GRADIENT_DELAY,
    GRADIENT_LEAVE_CURVE,
} from "../animation-constants";

const AUTODISMISS_TIMEOUT_SECONDS = 6;
const TRACKED_TAG = {
    "A": true,
    "BUTTON": true
}

@Component({
    selector: "vdk-toast",
    templateUrl: "./toast.component.html",
    styleUrls: ["./toast.component.scss"],
    animations: [
        trigger('launchToast', [
            transition(':enter', [
                // toast parent element animation
                group([
                    style({
                        transform: 'translateX(48px) scale(0, 1)'
                    }),
                    animate(`${multiply(componentPrimaryEnterTiming)}ms ${componentPrimaryEnterCurve}`, style({
                        transform: 'translateX(0) scale(1, 1)'
                    })),

                    // use optional: true for if/else elements
                    query('.checkmark', animateChild(), {optional: true}),
                    query('#info-icon-dot', animateChild(), {optional: true}),
                    query('#info-icon-line', animateChild(), {optional: true}),
                    query('#warn-icon-dot', animateChild(), {optional: true}),
                    query('#warn-icon-line', animateChild(), {optional: true}),
                    query('#error-icon-dot', animateChild(), {optional: true}),
                    query('#error-icon-line', animateChild(), {optional: true}),
                    query('.gradient', animateChild()),
                    query('.dismiss', animateChild(), { optional: true }),
                ]),
            ]),

            // START LEAVE ANIMATION
            // ':leave' is a default state for ngIf and ngFor, doesn't need to be predefined
            transition(':leave', [
                group([
                    style({
                        transform: 'translateX(0px) scale(1, 1)',
                        marginTop: '*',
                    }),

                    // use query self to be able to group the animation on the current element
                    query(':self', [
                        animate(`${multiply(componentPrimaryLeaveTiming)}ms ${componentPrimaryLeaveCurve}`, style({
                            transform: 'translateX(18px) scale(0, 1)'
                        })),

                        animate(`${multiply(componentPrimaryLeaveTiming)}ms ${componentPrimaryLeaveCurve}`, style({
                            marginTop: '-{{height}}px'
                        })),
                    ]),

                    query('.toast-description, .toast-title, .icon, .button-container, .dismiss-bg, .dismiss, .toast-date', [
                        animate(`${multiply(10)}ms`, style({
                            opacity: '0'
                        })),
                    ]),

                ]),
            ], {
                params: {
                   height: 0
                }
            }),
        // end launchToast
        ]),


        // info icon animation
        trigger('infoLine', [
            transition('* => *', [
                animate(`${multiply(linePrimaryEnterTiming)}ms ${multiply(linePrimaryEnterDelay)}ms ${linePrimaryEnterCurve}`, keyframes([
                    style({ strokeDashoffset: '16', offset: 0 }),
                    style({ strokeDashoffset: '0', offset: 1.0}),
               ]))
            ]),
        ]),
        trigger('infoDot', [
            transition('* => *', [
                style({
                    transform: 'scale(0)'
                }),
                animate(`${multiply(lineSecondaryEnterTiming)}ms ${multiply(lineSecondaryEnterDelay)}ms ${lineSecondaryEnterCurve}`, style({
                    transform: 'scale(1)'
                }))
            ]),
        ]),

        // error icon animation
        trigger('errorLine', [
            transition('* => *', [
                animate(`${multiply(linePrimaryEnterTiming)}ms ${multiply(linePrimaryEnterDelay)}ms ${linePrimaryEnterCurve}`, keyframes([
                    style({ strokeDashoffset: '7.919999599456787', offset: 0 }),
                    style({ strokeDashoffset: '0', offset: 1.0}),
               ]))
            ]),
        ]),
        trigger('errorDot', [
            transition('* => *', [
                style({
                    transform: 'scale(0)'
                }),
                animate(`${multiply(lineSecondaryEnterTiming)}ms ${multiply(lineSecondaryEnterDelay)}ms ${lineSecondaryEnterCurve}`, style({
                    transform: 'scale(1)'
                }))
            ]),
        ]),

        //warning icon animation
        trigger('warnLine', [
            transition('* => *', [
                animate(`${multiply(linePrimaryEnterTiming)}ms ${multiply(linePrimaryEnterDelay)}ms ${linePrimaryEnterCurve}`, keyframes([
                    style({ strokeDashoffset: '7.919999599456787', offset: 0 }),
                    style({ strokeDashoffset: '0', offset: 1.0}),
               ]))
            ]),
        ]),
        trigger('warnDot', [
            transition('* => *', [
                style({
                    transform: 'scale(0)'
                }),
                animate(`${multiply(lineSecondaryEnterTiming)}ms ${multiply(lineSecondaryEnterDelay)}ms ${lineSecondaryEnterCurve}`, style({
                    transform: 'scale(1)'
                }))
            ]),
        ]),

        // success icon animation
        trigger('checkmarkLine', [
            transition('* => *', [
                // css keyframe animation
                animate(`${multiply(linePrimaryEnterTiming)}ms ${multiply(linePrimaryEnterDelay)}ms ${linePrimaryEnterCurve}`, keyframes([
                    style({ strokeDashoffset: '31.386688232421875', offset: 0 }),
                    style({ strokeDashoffset: '0', offset: 1.0}),
               ]))
            ]),
        ]),

        // moving the gradient offview
        trigger('gradientMove', [
            transition('* => *', [
                style({
                    transform: 'scale(1, 1)'
                }),
                animate(`${multiply(GRADIENT_DURATION)}ms ${multiply(GRADIENT_DELAY)}ms ${GRADIENT_LEAVE_CURVE}`, style({
                    transform: 'scale(0, 1)'
                }))
            ]),
        ]),

        // fade in the dismiss icon
        trigger('dismissIconVisible', [
            transition('* => *', [
                style({
                    opacity: '0'
                }),
                animate(`${multiply(DISMISS_ICON_DURATION)}ms ${multiply(DISMISS_ICON_DELAY)}ms ${DISMISS_ICON_CURVE}`, style({
                    opacity: '1'
                }))
            ]),
        ]),
    ]

})
export class VdkToastComponent {
    public mouseover = false;
    public focused = false;

    @Input() type: VmwToastType = VmwToastType.INFO;
    @Input() primaryButtonText: string;
    @Input() secondaryButtonText: string;
    @Input() dismissible: boolean = true;
    @Input() timeoutSeconds: number = AUTODISMISS_TIMEOUT_SECONDS;

    @Output() dismissed = new EventEmitter();
    @Output() primaryButtonClick = new EventEmitter();
    @Output() secondaryButtonClick = new EventEmitter();

    readonly VmwToastType = VmwToastType;
    disableAutoDismiss: boolean = false;
    height: number;
    animate = true;

    constructor(
        private element: ElementRef,
        private ngZone: NgZone,
        public translateService: VdkSimpleTranslateService,
        // @Optional() private segmentService,
        ) {
            this.translateService.loadTranslationsForComponent('toast', TRANSLATIONS);
    }

    ngOnInit() {
        this.setUpTimer();
    }

    @HostListener('click', ['$event'])
    trackClicks(event: any) {
        return;
    }

    mouseOver(over: boolean) {
        // If the user moves their mouse over the snack, disable auto-dismiss
        this.disableAutoDismiss = over;
    }

    focus(focused: boolean) {
        this.disableAutoDismiss = focused;
    }

    get loaded() {
        return {
            value: this.animate,
            params: {
                height: this.element.nativeElement.clientHeight
            }
        };
    }

    dismiss(userDismissed: boolean = false) {
        this.animate = false;

        // before we tell the app to remove the toast, give the leave animation
        // some time to run...
        timer(multiply(componentPrimaryLeaveTiming + 200)).pipe(take(1)).subscribe(() => {
            this.dismissed.emit();
        });
    }

    private setUpTimer() {
        if (this.timeoutSeconds > 0) {
            this.ngZone.runOutsideAngular(() => {
                timer(this.timeoutSeconds * multiply(1000)).pipe(take(1)).subscribe(() => {
                    this.ngZone.run(() => {
                        if (this.disableAutoDismiss) {
                            this.setUpTimer();
                            return;
                        }
                        this.dismiss();
                    });
                });
            });
        }
    }
}
