/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';

import { ClipboardService } from 'ngx-clipboard';

import { VmwToastType } from '../../../commons';

import { TaurusObject } from '../../../common';

import { Toast } from '../model';
import { ToastService } from '../service';

interface ToastInternal extends Toast {
    id: number;
    time: Date;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    error?: any;
}

@Component({
    selector: 'shared-toasts',
    templateUrl: './toasts.component.html',
    styleUrls: ['./toasts.component.scss']
})
export class ToastsComponent extends TaurusObject implements OnInit {
    private static toastMessageCounter = 0;

    toasts: ToastInternal[];

    constructor(private readonly toastService: ToastService,
                private readonly clipboardService: ClipboardService) {
        super();
        this.toasts = [];
    }

    /**
     * ** Optimize Toast rendering using tracking with auto incremented ID per Toast.
     */
    trackByRendering(_index: number, toast: ToastInternal): number {
        return toast.id;
    }

    /**
     * ** Returns if Toast with given index is expanded.
     */
    isToastExpanded(index: number): boolean {
        return this.toasts[index].expanded;
    }

    /**
     * ** Evaluate if recommendation text for Copy and Report is visible.
     */
    isReportRecommendationVisible(toast: ToastInternal, index: number): boolean {
        return this.isToastExpanded(index) &&
            this._isTypeError(toast) &&
            toast.responseStatus !== 500;
    }

    /**
     * ** Remove Toast message.
     */
    removeToast(index: number): void {
        this.toasts.splice(index, 1);
    }

    /**
     * ** Toggle Toast expand details (expand/collapse).
     */
    toggleToastExpandDetails(index: number): void {
        this.toasts[index].expanded = !this.toasts[index].expanded;
    }

    /**
     * ** Copy to clipboard provided object.
     */
    copyToClipboard(copy: ToastInternal): void {
        try {
            this.clipboardService.copy(JSON.stringify(copy));
        } catch (e) {
            console.error(e);

            this._handleCopyActionError();
        }
    }

    /**
     * ** Returns Toast timeout in unit seconds.
     */
    getTimeout(toast: ToastInternal): number {
        return this._isTypeError(toast)
            ? 30
            : 5;
    }

    /**
     * ** Returns text for Btn CopyToClipboard.
     */
    getCopyToClipboardBtnText(toast: ToastInternal): string {
        return this._isTypeError(toast)
            ? 'Copy to clipboard'
            : '';
    }

    /**
     * ** Returns text for Btn Expand/Collapse.
     */
    getExpandBtnText(toast: ToastInternal, index: number): string {
        if (this._isTypeError(toast)) {
            return this.isToastExpanded(index)
                ? 'less'
                : 'more';
        }

        return '';
    }

    /**
     * @inheritDoc
     */
    ngOnInit() {
        this.subscriptions.push(
            this.toastService
                .getNotifications()
                .subscribe((toast: Toast) => {
                    this.toasts.push({
                        ...toast,
                        id: ToastsComponent.generateID(),
                        time: ToastsComponent.getDateTimeNow()
                    });
                }),
            this.clipboardService
                .copyResponse$
                .subscribe((result) => {
                    if (!result.isSuccess) {
                        this._handleCopyActionError();
                    }
                })
        );
    }

    private _isTypeError(toast: Toast): boolean {
        return toast.type === VmwToastType.FAILURE && !!toast.error;
    }

    private _handleCopyActionError(): void {
        this.toasts.push({
            type: VmwToastType.FAILURE,
            title: `Copy to clipboard`,
            description: `The view definition failed to copy to the clipboard`,
            id: ToastsComponent.generateID(),
            time: ToastsComponent.getDateTimeNow()
        });
    }

    /* eslint-disable @typescript-eslint/member-ordering */
    private static generateID(): number {
        return this.toastMessageCounter++;
    }

    private static getDateTimeNow(): Date {
        return new Date();
    }
}
