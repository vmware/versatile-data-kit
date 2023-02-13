/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

export interface ModalOptions {
    opened: boolean;
    title: string;
    message: string;
    cancelBtn: string;
    showCancelBtn: boolean;
    okBtn: string;
    showOkBtn: boolean;
    showCloseX: boolean;

    infoText?: string;
    warningText?: string;
}

export class DeleteModalOptions implements ModalOptions {
    opened: boolean;
    title: string;
    message: string;
    cancelBtn: string;
    showCancelBtn: boolean;
    okBtn: string;
    showOkBtn: boolean;
    showCloseX: boolean;

    constructor() {
        this.opened = false;
        this.title = 'Delete';
        this.message = 'Are you sure you want to permanently delete this item?';
        this.cancelBtn = 'Cancel';
        this.showCancelBtn = true;
        this.okBtn = 'Delete';
        this.showOkBtn = true;
        this.showCloseX = true;
    }
}

export class EditModalOptions implements ModalOptions {
    opened: boolean;
    title: string;
    message: string;
    cancelBtn: string;
    showCancelBtn: boolean;
    okBtn: string;
    showOkBtn: boolean;
    showCloseX: boolean;

    constructor() {
        this.opened = false;
        this.title = 'Edit';
        this.message = '';
        this.cancelBtn = 'Cancel';
        this.showCancelBtn = true;
        this.okBtn = 'Edit';
        this.showOkBtn = true;
        this.showCloseX = true;
    }
}

export class ConfirmationModalOptions implements ModalOptions {
    opened: boolean;
    title: string;
    message: string;
    cancelBtn: string;
    showCancelBtn: boolean;
    okBtn: string;
    showOkBtn: boolean;
    showCloseX: boolean;

    constructor() {
        this.opened = false;
        this.title = 'Confirm';
        this.message = 'Are you sure?';
        this.cancelBtn = 'Cancel';
        this.showCancelBtn = true;
        this.okBtn = 'Confirm';
        this.showOkBtn = true;
        this.showCloseX = true;
    }
}
